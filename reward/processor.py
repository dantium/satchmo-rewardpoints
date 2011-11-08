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

    def capture_payment(self, testing=False, order=None, amount=None):
        """
        Process the transaction and return a ProcessorResponse
        """
        if not order:
            order = self.order

        if amount is None:
            amount = order.balance

        payment = None

        if self.order.paid_in_full:
            success = True
            reason_code = "0"
            response_text = _("No balance to pay")
            self.record_payment()

        else:
            #contact = Contact.objects.from_request(request)
            reward, created = Reward.objects.get_or_create(contact=order.contact)
            
            point_modifier = config_value('PAYMENT_REWARD', 'POINTS_VALUE')
            total_point_value = point_modifier * reward.points
            
            if total_point_value > order.balance:
                point_value_used = order.balance
                points_used = point_value_used / point_modifier
            else:
                points_used = reward.points
                point_value_used = total_point_value
                
            orderpayment = self.record_payment(order=order, amount=point_value_used)
            reward_item = RewardItem.objects.add_order_payment(reward,order,orderpayment,points_used,point_value_used)

            reason_code = "0"
            response_text = _("Success")
            success = True

            if not self.order.paid_in_full:
                url = reverse('satchmo_balance_remaining')
                response_text = _("%s balance remains after using points") % moneyfmt(self.order.balance)

            return ProcessorResult(self.key, success, response_text, payment=payment)
