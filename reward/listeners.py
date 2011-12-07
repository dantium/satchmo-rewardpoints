import math

from livesettings import config_value
from satchmo_store.shop.models import Order
from satchmo_store.accounts.forms import RegistrationForm
from django.utils.translation import ugettext as _

from reward.models import Reward, RewardItem, POINTS_PENDING, POINTS_ADDED, POINTS_DEDUCTED

import logging

log = logging.getLogger('rewards.listeners')


def create_reward(contact, subscribed):
    """
    On creation of a customer account create rewards for them and add intial points if any.
    """
    log.debug("Caught registration, adding reward and initial customer points.")
    rewards_enabled = config_value('PAYMENT_REWARD', 'REWARD_ENABLE')
    if rewards_enabled:
        init_points = config_value('PAYMENT_REWARD', 'INITIAL_POINTS')
        reward = Reward.objects.create(contact=contact)
        if init_points > 0:
            point_item = RewardItem.objects.create(reward=reward, 
                                               points=init_points, 
                                               transaction_description="Initial Points", 
                                               status=POINTS_ADDED,
                                               )
        
def create_reward_listener(contact=None, subscribed=False, **kwargs):
    if contact:
        create_reward(contact, subscribed)
        

def add_points_on_order(order=None, **kwargs):
    log.debug("Caught order, attempting to add customer points pending.")
    rewards_enabled = config_value('PAYMENT_REWARD', 'REWARD_ENABLE')
    if order and rewards_enabled:
        if order.contact.user:
            if not RewardItem.objects.filter(order=order).filter(status=POINTS_PENDING).exists():
                #reward = Reward.objects.get_or_create(contact=order.contact)
                points = math.floor(order.sub_total * config_value('PAYMENT_REWARD', 'POINTS_EARNT') /100)
                RewardItem.objects.update_or_create(order.contact,order,points,POINTS_PENDING, _('Points from Order'))

def remove_points(order,oldstatus=None):
    log.debug("Caught order cancelled, attempting to remove customer points.")
    item = RewardItem.objects.get(order=order,orderpayment=None)
    if item:
        if oldstatus == "Complete":
            item.reward.points = item.reward.points - item.points
            item.reward.save()
        item.delete()
        
            
def add_points_on_complete(order):
    log.debug("Caught order Complete, attempting to add customer points .")

    try:
        item = RewardItem.objects.get(order=order,status=POINTS_PENDING)
        item.status = POINTS_ADDED
        item.save()
        item.reward.points = item.reward.points + item.points
        item.reward.save()
    except:
        log.debug("Can't change status of points")
            
def rcv_order_status_changed(oldstatus=None, newstatus=None, order=None, **kwargs):
    if order:
        if newstatus == "Complete":
            add_points_on_complete(order)
        if newstatus == "Cancelled":
            remove_points(order,oldstatus)
    


