from django.conf.urls import url

from .views import (
    EventDetail, EventList, CategoryEventList,
    YearEventList, MonthEventList, DayEventList,
    EventSearchResultsList)
from .feeds import LatestEventsFeed, CategoryFeed

urlpatterns = [
    url(r'^$',
        EventList.as_view(), name='event-list'),
    url(r'^feed/$', LatestEventsFeed(), name='event-list-feed'),

    url(r'^search/$',
        EventSearchResultsList.as_view(), name='event-search'),

    url(r'^(?P<year>\d{4})/$',
        YearEventList.as_view(), name='event-list-by-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        MonthEventList.as_view(), name='event-list-by-month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        DayEventList.as_view(), name='event-list-by-day'),

    # Various permalink styles that we support
    # ----------------------------------------
    # This supports permalinks with <event_pk>
    # NOTE: We cannot support /year/month/pk, /year/pk, or /pk, since these
    # patterns collide with the list/archive views, which we'd prefer to
    # continue to support.
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<pk>\d+)/$',
        EventDetail.as_view(), name='event-detail'),
    # These support permalinks with <event_slug>
    url(r'^(?P<slug>\w[-\w]*)/$',
        EventDetail.as_view(), name='event-detail'),
    url(r'^(?P<year>\d{4})/(?P<slug>\w[-\w]*)/$',
        EventDetail.as_view(), name='event-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        EventDetail.as_view(), name='event-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',  # flake8: NOQA
        EventDetail.as_view(), name='event-detail'),
    #spport download vCard
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<pk>\d+)/vcard/(?P<speaker_slug>\w[-\w]*)/$',
        EventDetail.as_view(), name='event-detail'),
    # These support permalinks with <event_slug>
    url(r'^(?P<slug>\w[-\w]*)/vcard/(?P<speaker_slug>\w[-\w]*)/$',
        EventDetail.as_view(), name='event-detail'),
    url(r'^(?P<year>\d{4})/(?P<slug>\w[-\w]*)/vcard/(?P<speaker_slug>\w[-\w]*)/$',
        EventDetail.as_view(), name='event-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/vcard/(?P<speaker_slug>\w[-\w]*)/$',
        EventDetail.as_view(), name='event-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/vcard/(?P<speaker_slug>\w[-\w]*)/$',  # flake8: NOQA
        EventDetail.as_view(), name='event-detail'),

    url(r'^category/(?P<category>\w[-\w]*)/$',
        CategoryEventList.as_view(), name='event-list-by-category'),
    url(r'^category/(?P<category>\w[-\w]*)/feed/$',
        CategoryFeed(), name='event-list-by-category-feed'),
]
