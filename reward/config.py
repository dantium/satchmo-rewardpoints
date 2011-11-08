from django.utils.translation import ugettext_lazy as _
from livesettings import *

gettext = lambda s: s

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_REWARD', _('Reward Points Settings'))

config_register_list(
                     
    BooleanValue(PAYMENT_GROUP,
        'REWARD_ENABLE',
        description= _("Enable Reward Points"),
        default=False
    ),
    
    BooleanValue(PAYMENT_GROUP,
        'REWARDS_NEED_TOTAL',
        description= _("If True points can't be used for Partial Payment"),
        default=False
    ),
    
    IntegerValue(PAYMENT_GROUP,
        'MIN_NEEDED',
        description=_("Minimum Points needed to be able to redeem on an order."),
        help_text=_("""Set to 0 to for no minimum"""),
        default=0,
    ),

    StringValue(PAYMENT_GROUP,
        'REWARD_SLUG',
        description=_("Rewards slug"),
        default="rewards"
    ),

    IntegerValue(PAYMENT_GROUP,
        'INITIAL_POINTS',
        description=_("Initial Points to Allocate to new customers"),
        help_text=_("""Set to 0 to prevent new customers from getting any points"""),
        default=0,
    ),

    DecimalValue(PAYMENT_GROUP,
        'POINTS_VALUE',
        description = _('Value of a point to the default Currency as used for redemption.'),
        default = 1,
    ),

    IntegerValue(PAYMENT_GROUP,
        'MIN_ORDER',
        description=_("Minimum Order Amount a customer can use to redeem points."),
        default=100,
    ),

    DecimalValue(PAYMENT_GROUP,
        'POINTS_EARNT',
        description=_("Amount of points earn't from purchase total as a percentage."),
        help_text=_("""If sent to 10% an order of 100 will gain the customer 10 points rounded up to the nearest whole figure."""),
        default=10,
    ),
    
    ModuleValue(PAYMENT_GROUP,
        'MODULE',
        description=_('Implementation module'),
        hidden=True,
        default = 'reward'),

    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'REWARD'),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'Points Payment',
        help_text = _('This will be passed to the translation utility')),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = '^points/'),
        
    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False)
)