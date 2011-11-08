from django.db import models

from django.utils.translation import ugettext_lazy as _
#from listeners import wishlist_cart_add_listener
from satchmo_store import shop
from satchmo_store.contact.models import Contact
from satchmo_store.shop.signals import cart_add_view
from satchmo_store.shop.models import Order
from signals_ahoy.signals import collect_urls
from livesettings import config_value


import datetime


POINTS_PENDING, POINTS_ADDED, POINTS_DEDUCTED, ORDER_PROCESSING = range(4)
STATUS_OPTIONS = (
    (POINTS_PENDING, _('Pending')),
    (POINTS_ADDED, _('Added')),
    (POINTS_DEDUCTED, _('Deducted')),
    (ORDER_PROCESSING, _('Processing')),
    )

class RewardManager(models.Manager):
    
    def points_list(self,contact):
        list = RewardItem.objects.filter(reward_contact=contact).exclude(status=ORDER_PROCESSING)
        return list
    
class Reward(models.Model):
    contact = models.ForeignKey(Contact, verbose_name=_("Contact"), related_name="reward",unique=True)
    points = models.IntegerField(verbose_name=_("Points"), default=0)
    created = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)
    
    objects = RewardManager()
    
    def _get_point_vaule(self):
        modifier = config_value('PAYMENT_REWARD', 'POINTS_VALUE')
        return modifier * self.points
    points_value = property(_get_point_vaule) 
        
    def _get_available_points(self):
        """ Calculate available points - pending """
         
        
    class Meta:
        verbose_name = _('Reward')
        verbose_name_plural = _('Rewards')
        
 
class RewardItemManager(models.Manager):
    """ When a customer uses points to make an order, delete from reward total and update status """
    def del_on_order(self,order):
        item = RewardItem.objects.get(order=order, status=POINTS_DEDUCTED)
        item.reward.points = item.reward.points - item.points
        item.reward.save()
        return item
    
    """ When an order is set to complete, add to reward total and update status """  
    def add_on_order_complete(self,order):
        item = RewardItem.objects.get(order=order, status=POINTS_ADDED)
        item.reward.points = item.reward.points + item.points
        item.reward.save()
        return item
    
    """ When an order payment is processed update status """  
    def add_order_payment(self,reward,order,orderpayment,points,points_value):
        item = RewardItem(reward=reward, orderpayment=orderpayment, points=points,points_value=points_value,status=POINTS_DEDUCTED)
        item.transaction_description = unicode(_("Redeemed points on Order"))
        item.save()
        return item
    
    def update_or_create(self,contact,order,points,status,desc):
        reward, created = Reward.objects.get_or_create(contact=contact)
        try:
            item = RewardItem.objects.get(order=order,reward=reward)
        except RewardItem.DoesNotExist:
            item = RewardItem(order=order,reward=reward)
        item.points = points
        item.status = status
        item.transaction_description = desc
        item.save()
        return item

    def from_order(self,order):
        item = RewardItem.objects.get(order=order)
        return item
        
class RewardItem(models.Model):
    reward = models.ForeignKey(Reward, verbose_name=_("Reward"), related_name="reward_items")
    points = models.IntegerField(verbose_name=_("Points"))
    points_value = models.IntegerField(verbose_name=_("Point Value"), blank=True, null=True)
    transaction_description = models.CharField(_("Transaction Description"), max_length=120, blank=True, null=True)
    order = models.ForeignKey(Order, verbose_name=_("Order"),  blank=True, null=True , unique=True)
    orderpayment = models.ForeignKey('shop.OrderPayment',  blank=True, null=True, verbose_name=_('Order Payment'))
    
    status = models.IntegerField(_("Status"),choices=STATUS_OPTIONS,)
    
    created = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)
    
    objects = RewardItemManager()
       
    def save(self, **kwargs):
        """ Update the customers total Points if initial save and status is not pending """
        if not self.pk:
            if self.status == POINTS_ADDED:
                self.reward.points = self.reward.points + self.points
                self.reward.save()
            if self.status == POINTS_DEDUCTED:
                self.reward.points = self.reward.points - self.points
                self.reward.save()
        super(RewardItem, self).save(**kwargs)
            
        
    class Meta:
        verbose_name = _('Reward Item')
        verbose_name_plural = _('Rewards Items')
        
import config
PAYMENT_PROCESSOR=True