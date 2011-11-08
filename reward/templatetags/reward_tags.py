from django import template
from django.template import TemplateSyntaxError
from livesettings import config_value

from satchmo_store.contact.models import Contact

from reward.models import Reward, RewardItem

register = template.Library()


def get_points_for_contact(contact):
    reward = Reward.objects.get(contact=contact)
    points = reward.points
    return points

class GetPoints(template.Node):
    def __init__(self, var):
        self.var = var
    def render(self, context):
        contact = Contact.objects.from_request(context['request'])
        context[self.var] = get_points_for_contact(contact)
        return ''
    
@register.tag 
def get_points(parser, token):
    try:
        tag_name, as_var, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires 2 arguments" % token.contents.split()[0])
    return GetPoints(var_name)


class GetPointModifier(template.Node):
    def __init__(self, var):
        self.var = var
    def render(self, context):
        context[self.var] = config_value('PAYMENT_REWARD', 'POINTS_VALUE')
        return ''
    
@register.tag 
def get_point_modifier(parser, token):
    try:
        tag_name, as_var, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires 2 arguments" % token.contents.split()[0])
    return GetPointModifier(var_name)

