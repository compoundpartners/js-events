# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
try:
    from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
except:
    SortedFilteredSelectMultiple = FilteredSelectMultiple
from aldryn_categories.models import Category
from aldryn_people.models import Person
from js_services.models import Service, ServicesConfig
from js_locations.models import Location
from . import models
from .cms_appconfig import EventsConfig
from .constants import RELATED_LAYOUTS, RELATED_SPEAKERS_LAYOUTS



TIME_PERIODS = [
    ('all', 'All'),
    ('future', 'Future'),
    ('past', 'Past'),
]


class EventRelatedPluginForm(forms.ModelForm):

    layout = forms.ChoiceField(choices=RELATED_LAYOUTS, required=False)
    time_period = forms.ChoiceField(choices=TIME_PERIODS)

    related_types = forms.ModelMultipleChoiceField(
        label='Related sections',
        queryset=EventsConfig.objects.exclude(namespace=EventsConfig.default_namespace),
        required=False,
        widget=FilteredSelectMultiple('Related sections', False)
    )
    related_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related categories', False)
    )
    related_service_sections = forms.ModelMultipleChoiceField(
        queryset=ServicesConfig.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related service sections', False)
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

class RelatedSpeakersPluginForm(forms.ModelForm):

    layout = forms.ChoiceField(choices=RELATED_SPEAKERS_LAYOUTS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['speakers'].widget = SortedFilteredSelectMultiple(attrs={'verbose_name': 'speaker'})
        self.fields['speakers'].queryset = models.Speaker.objects.all()
