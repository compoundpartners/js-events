# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from aldryn_categories.models import Category
from aldryn_people.models import Person
from js_services.models import Service
from .cms_appconfig import EventsConfig


LAYOUT_CHOICES = [
    ('cols', 'Columns'),
    ('rows', 'Rows'),
    ('hero', 'Hero'),
    ('events', 'Events'),
]

TIME_PERIODS = [
    ('all', 'All'),
    ('future', 'Future'),
    ('past', 'Past'),
]


class EventRelatedPluginForm(forms.ModelForm):

    layout = forms.ChoiceField(LAYOUT_CHOICES)
    time_period = forms.ChoiceField(TIME_PERIODS)

    related_types = forms.ModelMultipleChoiceField(
        label='Related sections',
        queryset=EventsConfig.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related sections', False)
    )
    related_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related categories', False)
    )
    related_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related services', False)
    )
    related_hosts = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related hosts', False)
    )

    class Meta:
        exclude = ['cache_duration']
