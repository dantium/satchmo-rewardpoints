from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.contrib import messages

from satchmo_utils.dynamic import lookup_url
from satchmo_store.contact.models import Contact
from livesettings import config_get_group, config_value
from product.models import Product
from satchmo_store.shop.models import Order
from payment.utils import pay_ship_save, get_or_create_order
from payment.views import confirm, payship
from l10n.utils import moneyfmt
from satchmo_store.shop.models import Order, OrderStatus

from reward.models import Reward, RewardItem

import logging

log = logging.getLogger('rewards.view')

payment_module = config_get_group('PAYMENT_REWARD')

""" Override controller to change remaining balance URL """
class RewardConfirmController(confirm.ConfirmController):
    
    def process(self):
        """Process a prepared payment"""
        result = self.processor.process(self.request)
        self.processorResults = result.success
        if result.payment:
            reason_code = result.payment.reason_code
        else:
            reason_code = ""
        self.processorReasonCode = reason_code
        self.processorMessage = result.message

        log.info("""Processing %s transaction with %s
        Order %i
        Results=%s
        Response=%s
        Reason=%s""", self.paymentModule.LABEL.value, self.paymentModule.KEY.value, 
                      self.order.id, self.processorResults, self.processorReasonCode, self.processorMessage)
        return self.processorResults
    
    def _onSuccess(self, controller):
        """Handles a success in payment.  If the order is paid-off, sends success, else return page to pay remaining."""
        if controller.order.paid_in_full:
            controller.cart.empty()
            for item in controller.order.orderitem_set.all():
                if item.product.is_subscription:
                    item.completed = True
                    item.save()
            try:
                curr_status = controller.order.orderstatus_set.latest()  
            except OrderStatus.DoesNotExist:
                curr_status = None
                
            if (curr_status is None) or (curr_status.notes and curr_status.status == "New"):
                controller.order.add_status(status='New', notes = "Order successfully submitted")
            else:
                # otherwise just update and save
                if not curr_status.notes:
                    curr_status.notes = _("Order successfully submitted")
                curr_status.save()                

            #Redirect to the success page
            url = controller.lookup_url('satchmo_checkout-success')
            return HttpResponseRedirect(url)    

        else:
            log.debug('Order #%i not paid in full, sending to pay rest of balance', controller.order.id)
            #url = controller.order.get_balance_remaining_url()
            url = reverse('satchmo_balance_remaining')
            return HttpResponseRedirect(url)

def pay_ship_info(request):
    return payship.base_pay_ship_info(request, payment_module, payship.simple_pay_ship_process_form,'shop/checkout/bank_transfer/pay_ship.html')
    

def confirm_info(request, template="shop/checkout/reward/confirm.html"):
    checkout_url = reverse('satchmo_checkout-step1')
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return HttpResponseRedirect(checkout_url)
    
    contact = Contact.objects.from_request(request)
    reward, created = Reward.objects.get_or_create(contact=contact)
    
    point_modifier = config_value('PAYMENT_REWARD', 'POINTS_VALUE')
    total_point_value = point_modifier * reward.points
    
    needs_total = config_value('PAYMENT_REWARD', 'REWARDS_NEED_TOTAL')
        
    if total_point_value > order.balance:
        point_value_used = order.balance
        points_used = point_value_used / point_modifier
    else:
        points_used = reward.points
        point_value_used = total_point_value
    
    controller = RewardConfirmController(request, payment_module)
    controller.templates['CONFIRM'] = template
    controller.extra_context={'points_used' : points_used, 'points_balance' : reward.points, 'needs_total':needs_total}
    controller.confirm()
    
    return controller.response


def point_history(request):
    try:
        contact = Contact.objects.from_request(request)
    except Contact.DoesNotExist:
        contact = None
    reward=None
    if contact:
        if config_value('PAYMENT_REWARD', 'REWARD_ENABLE'):
            reward, created = Reward.objects.get_or_create(contact=contact)
            
    ctx = RequestContext(request, {
        'reward' : reward,
    })

    return render_to_response('reward/point_list.html', context_instance=ctx)

reward_point_history = login_required(point_history)