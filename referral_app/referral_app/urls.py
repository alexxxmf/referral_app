from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.views.static import serve

from subscribers.views import (
    ConfirmationView,
    HomeView,
    MailChimpListenerView,
    DashboardView
)

# mailchimp_listener
urlpatterns = [
    url(r'^admin', admin.site.urls),
    # subscribers app
    url(
        r'^mc-listener$',
        MailChimpListenerView.as_view(),
        name='mailchimp_listener'
    ),
    url(
        r'^confirmation$',
        ConfirmationView.as_view(),
        name='confirmation_prompt'
    ),
    url(
        r'^dashboard/(?P<ref_code>\S+)',
        DashboardView.as_view(),
        name='dashboard'
    ),
    url(
        r'^$',
        HomeView.as_view(),
        name='home'
    ),
    url(
        r'^(?P<ref_code>\S+)$',
        HomeView.as_view(),
        name='home_when_referred'
    ),
]

if settings.DEBUG is True:
    static_view = never_cache(serve)
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$',
            static_view,
            {'document_root': settings.MEDIA_ROOT}
        ),

        url(
            r'^static/(?P<path>.*)$',
            static_view,
            {'document_root': settings.STATIC_ROOT}
        )
    ]

# why if i change the order of this list all gets messy in tests???
