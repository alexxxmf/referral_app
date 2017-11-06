from django.contrib import admin
from django.utils.html import format_html


from .models import Reward


class RewardAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'description',
        'image',
        'referrals_needed',
        'image_preview'
    )

    def image_preview(self, obj):
        # ImageField inherits from FileField
        if obj.image:
            return format_html(
                '<img src="%s" / style="max-width:150px">' % obj.image.url
            )
        else:
            return '(No image)'
    image_preview.image_preview = 'Image preview'

admin.site.register(Reward, RewardAdmin)
