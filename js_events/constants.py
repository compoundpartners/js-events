# -*- coding: utf-8 -*-

from django.conf import settings

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

try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
