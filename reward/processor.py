"""
Reward Payment processor
"""
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from l10n.utils import moneyfmt
from models import Reward, RewardItem, POINTS_DEDUCTED, ORDER_PROCESSING
from payment.modules.base import BasePaymentProcessor, ProcessorResult
from satchmo_store.contact.models import Contact
from livesettings import config_get_group, config_value

   
class PaymentProcessor(BasePaymentProcessor):

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('rewardpoints', settings)
        
    def process(self, request, testing=False):
        """This will process the payment."""
        if self.can_authorize() and not self.settings.CAPTURE.value:
            self.log_extra('Authorizing payment on order #%i', self.order.id)
            return self.authorize_payment(testing=testing)
        else:
            self.log_extra('Capturing payment on order #%i', self.order.id)
            return self.capture_payment(request, testing=testing)

    def capture_payment(self, request,testing=False, order=None, amount=None):
        """
        Process the transaction and return a ProcessorResponse
        """
        
        if not order:
            order = self.order

        if amount is None:
            amount = order.balance

        payment = None

        points = int(request.POST.get('points',None))
        
        if self.order.paid_in_full:
            success = True
            reason_code = "0"
            response_text = _("No balance to pay")
            self.record_payment()

        else:
            #contact = Contact.objects.from_request(request)
            if points:
                reward, created = Reward.objects.get_or_create(contact=order.contact)
                
                if points > reward.points:
                    success = False
                    reason_code = "0"
                    response_text = _("You Do not have that many reward points.")
                    return ProcessorResult(self.key, success, response_text, payment=payment)
                    
                
                point_modifier = config_value('PAYMENT_REWARD', 'POINTS_VALUE')
                point_value = point_modifier * points

                if point_value > order.balance:
                    success = False
                    reason_code = "0"
                    response_text = _("You are trying to use too many points for this order.")
                    return ProcessorResult(self.key, success, response_text, payment=payment)
                else:
                    points_used = points
                    point_value_used = point_value
                    
                    orderpayment = self.record_payment(order=order, amount=point_value_used)
                    reward_item = RewardItem.objects.add_order_payment(reward,order,orderpayment,points_used,point_value_used)
        
                    reason_code = "0"
                    response_text = _("Success")
                    success = True
    
                if not self.order.paid_in_full:
                    url = reverse('satchmo_balance_remaining')
                    response_text = _("%s balance remains after using points") % moneyfmt(self.order.balance)
            else:
                success = False
                reason_code = "0"
                response_text = _("Please enter the ammount of reward points you want to redeem")
                

        return ProcessorResult(self.key, success, response_text, payment=payment)
