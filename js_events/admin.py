# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from aldryn_people.models import Person
from aldryn_translation_tools.admin import AllTranslationsMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple

from . import models

from .constants import (
    EVENTS_SUMMARY_RICHTEXT,
)

from cms.admin.placeholderadmin import PlaceholderAdminMixin


def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)


make_published.short_description = _(
    "Mark selected events as published")


def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)


make_unpublished.short_description = _(
    "Mark selected events as not published")


def make_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)


make_featured.short_description = _(
    "Mark selected events as featured")


def make_not_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)


make_not_featured.short_description = _(
    "Mark selected events as not featured")


class EventAdminForm(TranslatableModelForm):

    class Meta:
        model = models.Event
        fields = [
            'app_config',
            'categories',
            'companies',
            'featured_image',
            'is_featured',
            'is_published',
            'lead_in',
            'location',
            'latitude',
            'longitude',
            'host',
            'host_2',
            'host_3',
            'event_start',
            'event_end',
            'registration_until',
            'registration_link',
            'external_link',
            'meta_description',
            'meta_keywords',
            'meta_title',
            'slug',
            'services',
            'title',
        ]

    def __init__(self, *args, **kwargs):
        super(EventAdminForm, self).__init__(*args, **kwargs)

        if not EVENTS_SUMMARY_RICHTEXT:
            self.fields['lead_in'].widget = widgets.Textarea()
            self.fields['location'].widget = widgets.Textarea()


class EventAdmin(
    PlaceholderAdminMixin,
    FrontendEditableAdminMixin,
    ModelAppHookConfig,
    TranslatableAdmin
):
    form = EventAdminForm
    list_display = ('title_view', 'app_config', 'event_start', 'is_featured',
                    'is_published')
    list_filter = [
        'app_config',
        'categories',
        'services',
        'companies',
    ]
    actions = (
        make_featured, make_not_featured,
        make_published, make_unpublished,
    )
    def title_view(self, obj):
         return obj.title
    title_view.short_description  = 'title'
    title_view.admin_order_field = 'translations__title'

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'lead_in',
                'featured_image',
                'location',
                ('latitude', 'longitude'),
                'host',
                'host_2',
                'host_3',
                'event_start',
                'event_end',
                'registration_until',
                'registration_link',
                'external_link',

                'publishing_date',
                'is_published',
                'is_featured',
            )
        }),
        (_('Meta Options'), {
            'classes': ('collapse',),
            'fields': (
                'slug',
                'meta_title',
                'meta_description',
                'meta_keywords',
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'categories',
                'services',
                'companies',
                'app_config',
            )
        }),
    )



    filter_horizontal = [
        'categories',
    ]
    app_config_values = {
        'default_published': 'is_published'
    }
    app_config_selection_title = ''
    app_config_selection_desc = ''

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'services':
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': 'service', 'verbose_name_plural': 'services'})
        if db_field.name == 'companies':
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': 'company', 'verbose_name_plural': 'companies'})
        return super(EventAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(models.Event, EventAdmin)


class EventsConfigAdmin(
    PlaceholderAdminMixin,
    BaseAppHookConfig,
    TranslatableAdmin
):
    def get_config_fields(self):
        return (
            'app_title', 'permalink_type', 'non_permalink_handling',
            'template_prefix', 'paginate_by', 'pagination_pages_start',
            'pagination_pages_visible', 'exclude_featured',
            'search_indexed', 'config.default_published',)


admin.site.register(models.EventsConfig, EventsConfigAdmin)
