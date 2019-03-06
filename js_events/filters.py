# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.timezone import now
from django import forms
from .cms_appconfig import EventsConfig
import django_filters
from . import models

TIME_PERIODS = [
    ('upcoming', 'Upcoming'),
    ('past', 'Past'),
]

class DateFilter(django_filters.ChoiceFilter):

    def filter(self, qs, value):
        if value == 'past':
            self.lookup_expr = 'lte'
        value = now()
        return super(DateFilter, self).filter(qs, value)


class EventFilters(django_filters.FilterSet):
    types = django_filters.ModelChoiceFilter('app_config', queryset=EventsConfig.objects.all())
    date = DateFilter('event_start', 'gt')

    class Meta:
        model = models.Event
        fields = ['types', 'date']

    def __init__(self, values, *args, **kwargs):
        super(EventFilters, self).__init__(values, *args, **kwargs)
        self.filters['types'].extra.update({'empty_label': 'by type'})
        self.filters['date'].extra.update({'empty_label': None})
        self.filters['date'].extra.update({'choices': TIME_PERIODS})

