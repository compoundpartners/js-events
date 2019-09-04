# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from aldryn_people.models import Person
from aldryn_translation_tools.admin import AllTranslationsMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db.models import SlugField
from django.forms import widgets
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple

from . import models

from .constants import (
    EVENTS_SUMMARY_RICHTEXT,
    EVENTS_ENABLE_PRICE,
    EVENTS_ENABLE_CPD,
    IS_THERE_COMPANIES,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

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
    companies = forms.CharField()

    class Meta:
        model = models.Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EventAdminForm, self).__init__(*args, **kwargs)

        if not EVENTS_SUMMARY_RICHTEXT:
            self.fields['lead_in'].widget = widgets.Textarea()
            self.fields['location'].widget = widgets.Textarea()
        if IS_THERE_COMPANIES:
            self.fields['companies'] = forms.ModelMultipleChoiceField(queryset=Company.objects.all(), required=False)# self.instance.companies
            self.fields['companies'].widget = SortedFilteredSelectMultiple()
            self.fields['companies'].queryset = Company.objects.all()
            if self.instance.pk and self.instance.companies.count():
                self.fields['companies'].initial = self.instance.companies.all()
        else:
            del self.fields['companies']


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
        'locations',
    ]
    actions = (
        make_featured, make_not_featured,
        make_published, make_unpublished,
    )
    def title_view(self, obj):
         return obj.title
    title_view.short_description  = 'title'
    title_view.admin_order_field = 'translations__title'

    extra_fields = (
    )

    if EVENTS_ENABLE_PRICE:
        extra_fields += (
            'price',
        )

    if EVENTS_ENABLE_CPD:
        extra_fields += (
            'cpd_points',
        )

    advanced_fields = (
        'categories',
        'services',
        'locations',
    )
    if IS_THERE_COMPANIES:
        advanced_fields += (
            'companies',
        )
    advanced_fields += (
        'app_config',
    )

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'lead_in',
                'featured_image',
                'location',
                'display_location',
                ('latitude', 'longitude'),
                'host',
                'host_2',
                'host_3',
                'event_start',
                'event_end',
                'registration_until',
                'registration_link',
                'redirect_url',
                'link_text',
                'publishing_date',
                'is_published',
                'is_featured',
                'hero_event',
                extra_fields
            )
        }),
        (_('Meta Options'), {
            'classes': ('collapse',),
            'fields': (
                'slug',
                'meta_title',
                'meta_description',
                'meta_keywords',
                'show_on_sitemap',
                'show_on_xml_sitemap',
                'noindex',
                'nofollow',
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': advanced_fields
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
        if db_field.name == 'locations':
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': 'location'})
        if db_field.name == 'companies':
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': 'company', 'verbose_name_plural': 'companies'})
        return super(EventAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'app_config':
            kwargs["queryset"] = models.EventsConfig.objects.exclude(namespace=models.EventsConfig.default_namespace)
        return super(EventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if IS_THERE_COMPANIES:
            obj.companies = Company.objects.filter(pk__in=form.cleaned_data.get('companies'))

admin.site.register(models.Event, EventAdmin)


class EventsConfigAdmin(
    PlaceholderAdminMixin,
    BaseAppHookConfig,
    TranslatableAdmin
):
    def get_config_fields(self):
        return (
            'app_title', 'allow_post', 'permalink_type', 'non_permalink_handling',
            'template_prefix', 'paginate_by', 'pagination_pages_start',
            'pagination_pages_visible', 'exclude_featured',
            'search_indexed', 'config.default_published',)


admin.site.register(models.EventsConfig, EventsConfigAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_published', 'company')
    search_fields = ('first_name', 'last_name')
    prepopulated_fields = {'slug': ('first_name', 'last_name')}
    #formfield_overrides = {
        #SlugField: {'widget': widgets.HiddenInput},
    #}


admin.site.register(models.Speaker, SpeakerAdmin)
