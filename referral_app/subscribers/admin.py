from django.contrib import admin

from .models import Subscriber


class SubscriberAdmin(admin.ModelAdmin):

    list_display = (
    	'email',
    	'email_from_referrer',
    	'confirmed_subscription',
    	'ip',
    	'referral_count',
    	'referred',
    	'unique_code',
    )


admin.site.register(Subscriber, SubscriberAdmin)
