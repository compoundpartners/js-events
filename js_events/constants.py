# -*- coding: utf-8 -*-

from django.conf import settings

EVENTS_HIDE_RELATED_EVENTS = getattr(
    settings,
    'EVENTS_HIDE_RELATED_EVENTS',
    False,
)
EVENTS_SUMMARY_RICHTEXT = getattr(
    settings,
    'EVENTS_SUMMARY_RICHTEXT',
    False,
)
