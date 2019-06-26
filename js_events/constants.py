# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.text import slugify

UPDATE_SEARCH_DATA_ON_SAVE = getattr(
    settings,
    'EVENTS_UPDATE_SEARCH_DATA_ON_SAVE',
    False,
)
EVENTS_SUMMARY_RICHTEXT = getattr(
    settings,
    'EVENTS_SUMMARY_RICHTEXT',
    False,
)
EVENTS_ENABLE_PRICE = getattr(
    settings,
    'EVENTS_ENABLE_PRICE',
    True,
)
EVENTS_ENABLE_CPD = getattr(
    settings,
    'EVENTS_ENABLE_CPD',
    True,
)
ADD_FILTERED_CATEGORIES = getattr(
    settings,
    'EVENTS_ADD_FILTERED_CATEGORIES',
    [],
)
ADDITIONAL_EXCLUDE = getattr(
    settings,
    'EVENTS_ADDITIONAL_EXCLUDE',
    {},
)
EVENTS_RELATED_LAYOUTS = getattr(
    settings,
    'EVENTS_RELATED_LAYOUTS',
    (),
)
if EVENTS_RELATED_LAYOUTS:
    RELATED_LAYOUTS = list(zip(map(lambda s: slugify(s).replace('-', '_'), EVENTS_RELATED_LAYOUTS), EVENTS_RELATED_LAYOUTS))
else:
    RELATED_LAYOUTS = (
        ('cols', 'Columns'),
        ('rows', 'Rows'),
        ('hero', 'Hero'),
        ('events', 'Events'),
        ('filter', 'Filter'),
    )

try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
