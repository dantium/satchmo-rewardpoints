from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _

from reward.models import Reward, RewardItem


class RewardItem_Inline(admin.TabularInline):
    model = RewardItem
    extra = 1

class RewardAdmin(admin.ModelAdmin):
    list_display = ['contact', 'points','created',]
    list_display_links = ('points',)
    ordering = ['created',]
    inlines = [RewardItem_Inline]

admin.site.register(Reward, RewardAdmin)

