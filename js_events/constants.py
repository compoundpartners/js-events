# -*- coding: utf-8 -*-

from django.conf import settings

EVENTS_SUMMARY_RICHTEXT = getattr(
    settings,
    'EVENTS_SUMMARY_RICHTEXT',
    False,
)
