# -*- coding: utf-8 -*-

from django.conf import settings

EVENTS_SUMMARY_RICHTEXT = getattr(
    settings,
    'EVENTS_SUMMARY_RICHTEXT',
    False,
)

try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
