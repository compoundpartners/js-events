# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.text import slugify

def get_template_choices(templates):
    values = list(templates).copy()
    # set first template as default
    if len(values):
        values[0] = ''
    return list(zip(map(lambda s: slugify(s).replace('-', '_'), values), templates))

def get_template_title(choices, template):
    default = choices[0][1] if len(choices) and (choices[0]) == 2 else 'Default'
    return dict(choices).get(template, default)

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
SHOW_RELATED_IMAGE = getattr(
    settings,
    'EVENTS_SHOW_RELATED_IMAGE',
    False,
)
ADD_FILTERED_CATEGORIES = getattr(
    settings,
    'EVENTS_ADD_FILTERED_CATEGORIES',
    [],
)
DEFAULT_FILTERS = getattr(
    settings,
    'EVENTS_DEFAULT_FILTERS',
    {},
)
ADDITIONAL_EXCLUDE = getattr(
    settings,
    'EVENTS_ADDITIONAL_EXCLUDE',
    {},
)

EVENT_TEMPLATES = [['', 'Default']] + list(getattr(
    settings,
    'EVENT_TEMPLATES',
    [],
))

EVENTS_RELATED_LAYOUTS = getattr(
    settings,
    'EVENTS_RELATED_LAYOUTS',
    [],
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

RELATED_SPEAKERS_LAYOUTS = getattr(
    settings,
    'EVENTS_RELATED_SPEAKERS_LAYOUTS',
    ['Default'],
)
RELATED_SPEAKERS_LAYOUTS = get_template_choices(RELATED_SPEAKERS_LAYOUTS)

GET_NEXT_EVENT = getattr(
    settings,
    'EVENTS_GET_NEXT_EVENT',
    False,
)

SITEMAP_CHANGEFREQ = getattr(
    settings,
    'EVENTS_SITEMAP_CHANGEFREQ',
    'never',
)
SITEMAP_PRIORITY = getattr(
    settings,
    'EVENTS_SITEMAP_PRIORITY',
    0.5,
)
RELATED_EVENTS_COUNT = getattr(
    settings,
    'EVENTS_RELATED_EVENTS_COUNT',
    None,
)
EVENT_CUSTOM_FIELDS = getattr(
    settings,
    'EVENTS_EVENT_CUSTOM_FIELDS',
    {},
)
EVENT_SECTION_CUSTOM_FIELDS = getattr(
    settings,
    'EVENTS_EVENT_SECTION_CUSTOM_FIELDS',
    {},
)
TRANSLATE_IS_PUBLISHED = getattr(
    settings,
    'EVENTS_TRANSLATE_IS_PUBLISHED',
    False,
)
TRANSLATE_CUSTOM_FIELDS = getattr(
    settings,
    'EVENTS_TRANSLATE_CUSTOM_FIELDS',
    False,
)
FILTER_EMPTY_LABELS = getattr(
    settings,
    'SEARCH_FILTER_EMPTY_LABELS',
    {}
)
FILTER_EMPTY_LABELS.update(getattr(
    settings,
    'EVENTS_FILTER_EMPTY_LABELS',
    {}
))

try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False

USE_CACHE = getattr(
    settings,
    'JUMPSUITE_USE_CACHE',
    {}
)