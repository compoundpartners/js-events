# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from aldryn_categories.models import Category
from aldryn_people.models import Person
from js_services.models import Service
from js_locations.models import Location
from .cms_appconfig import EventsConfig
from .constants import RELATED_LAYOUTS



TIME_PERIODS = [
    ('all', 'All'),
    ('future', 'Future'),
    ('past', 'Past'),
]


class EventRelatedPluginForm(forms.ModelForm):

    layout = forms.ChoiceField(RELATED_LAYOUTS)
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
    related_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related locations', False)
    )

    class Meta:
        exclude = ['cache_duration']
