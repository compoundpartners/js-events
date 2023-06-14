# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from aldryn_people.models import Person
from aldryn_translation_tools.admin import AllTranslationsMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from cms.utils.i18n import get_current_language, get_language_list
from cms.utils import copy_plugins, get_current_site
from django.db import transaction
from django.db.models import SlugField
from django.db.models.query import EmptyQuerySet
from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.sites.models import Site
from django.forms import widgets
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import mark_safe
from django.core.exceptions import PermissionDenied
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
try:
    from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
except:
    SortedFilteredSelectMultiple = FilteredSelectMultiple

from . import models

from .constants import (
    EVENTS_SUMMARY_RICHTEXT,
    EVENTS_ENABLE_PRICE,
    EVENTS_ENABLE_CPD,
    IS_THERE_COMPANIES,
    EVENT_TEMPLATES,
    EVENT_CUSTOM_FIELDS,
    EVENT_SECTION_CUSTOM_FIELDS,
    TRANSLATE_IS_PUBLISHED,
    TRANSLATE_CUSTOM_FIELDS,
    SHOW_RELATED_IMAGE,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

from cms.admin.placeholderadmin import PlaceholderAdminMixin

try:
    from js_custom_fields.forms import CustomFieldsFormMixin, CustomFieldsSettingsFormMixin
except:
    class CustomFieldsFormMixin(object):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'custom_fields' in self.fields:
                self.fields['custom_fields'].widget = forms.HiddenInput()

    class CustomFieldsSettingsFormMixin(object):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'custom_fields_settings' in self.fields:
                self.fields['custom_fields_settings'].widget = forms.HiddenInput()

require_POST = method_decorator(require_POST)

def make_published(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_published_trans = True
            i.save()
    else:
        queryset.update(is_published=True)

make_published.short_description = _(
    "Mark selected events as published")


def make_unpublished(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_published_trans = False
            i.save()
    else:
        queryset.update(is_published=False)

make_unpublished.short_description = _(
    "Mark selected events as not published")


def make_featured(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_featured_trans = True
            i.save()
    else:
        queryset.update(is_featured=True)

make_featured.short_description = _(
    "Mark selected events as featured")


def make_not_featured(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_featured_trans = False
            i.save()
    else:
        queryset.update(is_featured=False)

make_not_featured.short_description = _(
    "Mark selected events as not featured")


class EventAdminForm(CustomFieldsFormMixin, TranslatableModelForm):
    companies = forms.CharField()
    template = forms.ChoiceField(choices=EVENT_TEMPLATES, required=False)

    custom_fields = 'get_custom_fields'

    class Meta:
        model = models.Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        if TRANSLATE_CUSTOM_FIELDS:
            self.custom_fields_field_name = 'custom_fields_trans'

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
        if 'event_start' in self.fields:
            if self.instance and hasattr(self.instance, 'app_config'):
                self.fields['event_start'].required = self.instance.app_config.dates_required
            elif 'app_config' in self.initial:
                self.fields['event_start'].required = self.fields['app_config'].initial.dates_required
            elif len(args) > 0 and 'app_config' in args[0] and args[0]['app_config'].isnumeric():
                app_config = models.EventsConfig.objects.filter(pk=args[0]['app_config'])
                if app_config.count():
                    self.fields['event_start'].required = app_config[0].dates_required
                else:
                    self.fields['event_start'].required = True
            else:
                self.fields['event_start'].required = True

    def get_custom_fields(self):
        fields = EVENT_CUSTOM_FIELDS
        if self.instance and hasattr(self.instance, 'app_config') and self.instance.app_config.custom_fields_settings:
            fields.update(self.instance.app_config.custom_fields_settings)
        return fields


class EventAdmin(
    PlaceholderAdminMixin,
    FrontendEditableAdminMixin,
    ModelAppHookConfig,
    TranslatableAdmin
):
    def get_queryset(self, request):
        return self.model.all_objects.distinct()

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

    def is_published_trans_safe(self, obj):
        return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.safe_translation_getter('is_published_trans', default=False) else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    is_published_trans_safe.short_description = _('is published')

    def is_featured_trans_safe(self, obj):
        return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">' if obj.safe_translation_getter('is_featured_trans', default=False) else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    is_featured_trans_safe.short_description = _('is featured')

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
        'template',
    )

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'lead_in',
                'featured_image',
                'related_image' if SHOW_RELATED_IMAGE else (),
                'channel',
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
                extra_fields,
                'custom_fields',
            )
        }),
        (_('Meta Options'), {
            'classes': ('collapse',),
            'fields': (
                'slug',
                'meta_title',
                'meta_description',
                'meta_keywords',
                'share_image',
                'show_on_sitemap',
                'show_on_xml_sitemap',
                'noindex',
                'nofollow',
                'canonical_url',
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
    app_config_selection_title = ''
    app_config_selection_desc = ''

    def get_list_display(self, request):
        fields = []
        list_display = super().get_list_display(request)
        for field in list_display:
            if field  in ['is_published', 'is_featured'] and TRANSLATE_IS_PUBLISHED:
                field += '_trans_safe'
            fields.append(field)
        return fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        for fieldset in fieldsets:
            if len(fieldset) == 2 and 'fields' in fieldset[1]:
                fields = []
                for field in fieldset[1]['fields']:
                    if field  in ['is_published', 'is_featured'] and TRANSLATE_IS_PUBLISHED:
                        field += '_trans'
                    elif field  == 'custom_fields' and TRANSLATE_CUSTOM_FIELDS:
                        field += '_trans'
                    fields.append(field)
                fieldset[1]['fields'] = fields
        return fieldsets

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'services':
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': db_field.name})
        elif db_field.name == 'locations':
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': db_field.name})
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'app_config':
            kwargs["queryset"] = models.EventsConfig.objects.exclude(namespace=models.EventsConfig.default_namespace)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if IS_THERE_COMPANIES:
            obj.companies.set(Company.objects.filter(pk__in=form.cleaned_data.get('companies')))

    def get_site(self, request):
        site_id = request.session.get('cms_admin_site')
        if not site_id:
            return get_current_site()
        try:
            site = Site.objects._get_site_by_id(site_id)
        except Site.DoesNotExist:
            site = get_current_site()
        return site

    @require_POST
    @transaction.atomic
    def copy_language(self, request, obj_id):
        obj = self.get_object(request, object_id=obj_id)
        source_language = request.POST.get('source_language')
        target_language = request.POST.get('target_language')

        if not self.has_change_permission(request, obj=obj):
            raise PermissionDenied

        if obj is None:
            raise Http404

        if not target_language or not target_language in get_language_list(site_id=self.get_site(request).pk):
            return HttpResponseBadRequest(force_text(_("Language must be set to a supported language!")))

        for placeholder in obj.get_placeholders():
            plugins = list(
                placeholder.get_plugins(language=source_language).order_by('path'))
            if not placeholder.has_add_plugins_permission(request.user, plugins):
                return HttpResponseForbidden(force_text(_('You do not have permission to copy these plugins.')))
            copy_plugins.copy_plugins_to(plugins, placeholder, target_language)
        return HttpResponse("ok")

    def get_urls(self):
        urlpatterns = super().get_urls()
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        return [url(
            r'^(.+)/copy_language/$',
            self.admin_site.admin_view(self.copy_language),
            name='{0}_{1}_copy_language'.format(*info)
        )] + urlpatterns


admin.site.register(models.Event, EventAdmin)

class EventsConfigAdminForm(CustomFieldsFormMixin, CustomFieldsSettingsFormMixin, TranslatableModelForm):
    custom_fields = EVENT_SECTION_CUSTOM_FIELDS



class EventsConfigAdmin(
    PlaceholderAdminMixin,
    BaseAppHookConfig,
    TranslatableAdmin
):
    form = EventsConfigAdminForm

    def get_config_fields(self):
        return (
            'app_title', 'allow_post', 'permalink_type', 'non_permalink_handling',
            'template_prefix', 'paginate_by', 'pagination_pages_start',
            'pagination_pages_visible', 'exclude_featured',
            'search_indexed', 'show_in_listing', 'dates_required',
            'custom_fields_settings', 'custom_fields')

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

admin.site.register(models.EventsConfig, EventsConfigAdmin)


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_published', 'company')
    search_fields = ('first_name', 'last_name')
    prepopulated_fields = {'slug': ('first_name', 'last_name')}
    #formfield_overrides = {
        #SlugField: {'widget': widgets.HiddenInput},
    #}

admin.site.register(models.Speaker, SpeakerAdmin)

class ChannelAdminclass(TranslatableAdmin):
    fields = ['name', 'position']

admin.site.register(models.Channel, ChannelAdminclass)
