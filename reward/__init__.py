from satchmo_store.shop.signals import order_success, order_cancelled, satchmo_order_status_changed
from satchmo_store.accounts.signals import satchmo_registration
from satchmo_store.shop.models import Order
from satchmo_store.accounts.forms import RegistrationForm
from satchmo_store import shop
from signals_ahoy.signals import collect_urls

from reward.listeners import *
from reward.urls import add_reward_urls

log = logging.getLogger('rewards.listeners')

log.debug("Adding reward listeners")

satchmo_registration.connect(create_reward_listener, sender=None)
satchmo_order_status_changed.connect(rcv_order_status_changed, sender=None)
#order_cancelled.connect(remove_points, sender=None)
order_success.connect(add_points_on_order, sender=None)


collect_urls.connect(add_reward_urls, sender=shop)