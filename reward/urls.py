from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

import logging
log = logging.getLogger('reward.urls')

urlpatterns = patterns('',
     (r'^$', 'reward.views.pay_ship_info', {'SSL':ssl}, 'REWARD_satchmo_checkout-step2'),
     (r'^confirm/$', 'reward.views.confirm_info', {'SSL':ssl}, 'REWARD_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL':ssl}, 'REWARD_satchmo_checkout-success'),
     #(r'^balance/$', 'payment.modules.giftcertificate.views.check_balance', {'SSL':ssl}, 'satchmo_giftcertificate_balance'),
)


addurlpatterns = patterns('',
     (r'^point_history/$', 'reward.views.reward_point_history', {}, 'reward-history'),
)


def add_reward_urls(sender, patterns=(), section="", **kwargs):
    log.debug('adding reward urls')
    patterns += addurlpatterns