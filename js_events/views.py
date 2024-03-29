# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
)
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.utils.cache import patch_cache_control
from django.utils.timezone import now
from cms.cache.page import set_page_cache, get_page_cache
from cms.utils.compat import DJANGO_2_2, DJANGO_3_0

from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin, ViewUrlMixin
from taggit.models import Tag

from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_categories.models import Category
from aldryn_people.models import Person

from aldryn_newsblog.utils.utilities import get_valid_languages_from_request
from aldryn_newsblog.utils import add_prefix_to_path
from .cms_appconfig import EventsConfig
from .models import Event, Speaker
from .filters import EventFilters
from .constants import (
    DEFAULT_FILTERS, 
    GET_NEXT_EVENT, 
    RELATED_EVENTS_COUNT,
    USE_CACHE,
)

class NoneMixin(object):
    pass

try:
    from custom.js_events.views import CustomListMixin
except:
    CustomListMixin = NoneMixin
try:
    from custom.js_events.views import CustomDetailMixin
except:
    CustomDetailMixin = NoneMixin


class CachedMixin():
    def use_cache(self, request):
        is_authenticated = request.user.is_authenticated
        model_name = str(self.model.__name__ if self.model else self.queryset.model.__name__)
        return request.method.lower() == 'get' and model_name in USE_CACHE and USE_CACHE[model_name] and (
            not hasattr(request, 'toolbar') or (
                not request.toolbar.edit_mode_active and not request.toolbar.show_toolbar and not is_authenticated
            )
        )

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        response_timestamp = now()
        if self.use_cache(request):
            cache_content = get_page_cache(request)
            if cache_content is not None:
                content, headers, expires_datetime = cache_content
                response = HttpResponse(content)
                response.xframe_options_exempt = True
                if DJANGO_2_2 or DJANGO_3_0:
                    response._headers = headers
                else:
                    #  for django3.2 and above. response.headers replaces response._headers in earlier versions of django
                    response.headers = headers
                # Recalculate the max-age header for this cached response
                max_age = int(
                    (expires_datetime - response_timestamp).total_seconds() + 0.5)
                patch_cache_control(response, max_age=max_age)
                return response
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if self.use_cache(self.request):
            response.add_post_render_callback(set_page_cache)
        return response


class TemplatePrefixMixin(object):

    def prefix_template_names(self, template_names):
        if (hasattr(self.config, 'template_prefix') and
                self.config.template_prefix):
            prefix = self.config.template_prefix
            return [
                add_prefix_to_path(template, prefix)
                for template in template_names]
        return template_names

    def get_template_names(self):
        template_names = super(TemplatePrefixMixin, self).get_template_names()
        return self.prefix_template_names(template_names)


class EditModeMixin(object):
    """
    A mixin which sets the property 'edit_mode' with the truth value for
    whether a user is logged-into the CMS and is in edit-mode.
    """
    edit_mode = False

    def dispatch(self, request, *args, **kwargs):
        self.edit_mode = (
            self.request.toolbar and self.request.toolbar.edit_mode_active)
        return super(EditModeMixin, self).dispatch(request, *args, **kwargs)


class PreviewModeMixin(EditModeMixin):
    """
    If content editor is logged-in, show all events. Otherwise, only the
    published events should be returned.
    """
    def get_queryset(self):
        if self.namespace == EventsConfig.default_namespace:
            qs = self.model.objects
        else:
            qs = self.model.all_objects.namespace(self.namespace)
        # check if user can see unpublished items. this will allow to switch
        # to edit mode instead of 404 on event detail page. CMS handles the
        # permissions.
        user = self.request.user
        user_can_edit = user.is_staff or user.is_superuser
        if not (self.edit_mode or user_can_edit):
            qs = qs.published()
        language = translation.get_language()
        qs = qs.active_translations(language)
        return qs


class AppHookCheckMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.valid_languages = get_valid_languages_from_request(
            self.namespace, request)
        return super(AppHookCheckMixin, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        # filter available objects to contain only resolvable for current
        # language. IMPORTANT: after .translated - we cannot use .filter
        # on translated fields (parler/django limitation).
        # if your mixin contains filtering after super call - please place it
        # after this mixin.
        qs = super(AppHookCheckMixin, self).get_queryset()
        return qs#.translated(*self.valid_languages)


class EventDetail(CustomDetailMixin, CachedMixin, AppConfigMixin, AppHookCheckMixin, PreviewModeMixin,
                    TranslatableSlugMixin, TemplatePrefixMixin, DetailView):
    model = Event
    slug_field = 'slug'
    year_url_kwarg = 'year'
    month_url_kwarg = 'month'
    day_url_kwarg = 'day'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'

    def get(self, request, *args, **kwargs):
        # if 'speaker_slug' in kwargs:
            # speaker_slug = kwargs['speaker_slug']
            # speaker = Speaker.objects.published().filter(slug=speaker_slug, vcard_enabled=True)
            # if speaker.count() != 1:
                # raise Http404
            # filename = "%s.vcf" % str(speaker_slug)
            # vcard = speaker[0].get_vcard(request)
            # try:
                # vcard = vcard.decode('utf-8').encode('ISO-8859-1')
            # except UnicodeError:
                # pass
            # response = HttpResponse(vcard, content_type="text/x-vCard")
            # response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
                # filename)
            # return response
        # """
        # This handles non-permalinked URLs according to preferences as set in
        # EventsConfig.
        # """
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        # set_language_changer(request, self.object.get_public_url)
        if self.object.redirect_url:
            return HttpResponseRedirect(self.object.redirect_url)

        # url = self.object.get_absolute_url()
        # if (self.config.non_permalink_handling == 200 or request.path == url):
        # Continue as normal
        #return super(EventDetail, self).get(request, *args, **kwargs)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

        # Check to see if the URL path matches the correct absolute_url of
        # the found object
        if self.config.non_permalink_handling == 302:
            return HttpResponseRedirect(url)
        elif self.config.non_permalink_handling == 301:
            return HttpResponsePermanentRedirect(url)
        else:
            raise Http404('This is not the canonical uri of this object.')

    def post(self, request, *args, **kwargs):
        if self.config.allow_post:
            return super(EventDetail, self).get(request, *args, **kwargs)
        else:
            return super(EventDetail, self).http_method_not_allowed(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """
        Supports ALL of the types of permalinks that we've defined in urls.py.
        However, it does require that either the id and the slug is available
        and unique.
        """
        if queryset is None:
            queryset = self.get_queryset()

        slug = self.kwargs.get(self.slug_url_kwarg, None)
        pk = self.kwargs.get(self.pk_url_kwarg, None)

        if pk is not None:
            # Let the DetailView itself handle this one
            return DetailView.get_object(self, queryset=queryset)
        elif slug is not None:
            # Let the TranslatedSlugMixin take over
            return super(EventDetail, self).get_object(queryset=queryset)

        raise AttributeError('EventDetail view must be called with either '
                             'an object pk or a slug')

    def get_context_data(self, **kwargs):
        context = super(EventDetail, self).get_context_data(**kwargs)
        if GET_NEXT_EVENT:
            context['prev_event'] = self.get_prev_object(
                self.queryset, self.object)
            context['next_event'] = self.get_next_object(
                self.queryset, self.object)

        event = context['event']

        if False:
            related_types_first = event.app_config
            if related_types_first is not None:
                context['related_types_first'] = related_types_first.namespace
            else:
                context['related_types_first'] = 'all'
            related_categories_first = event.categories.all().first()
            if related_categories_first is not None:
                context['related_categories_first'] = related_categories_first.slug
            else:
                context['related_categories_first'] = 'all'
        related_events = event.related_events
        if RELATED_EVENTS_COUNT:
            context['related_events'] = related_events[:RELATED_EVENTS_COUNT]
        else:
            context['related_events'] = related_events

        return context

    def get_prev_object(self, queryset=None, object=None):
        if queryset is None:
            queryset = self.get_queryset()
        if object is None:
            object = self.get_object(self)
        prev_objs = queryset.filter(
            publishing_date__lt=object.publishing_date
        ).order_by(
            '-publishing_date'
        )[:1]
        if prev_objs:
            return prev_objs[0]
        else:
            return None

    def get_next_object(self, queryset=None, object=None):
        if queryset is None:
            queryset = self.get_queryset()
        if object is None:
            object = self.get_object(self)
        next_objs = queryset.filter(
            publishing_date__gt=object.publishing_date
        ).order_by(
            'publishing_date'
        )[:1]
        if next_objs:
            return next_objs[0]
        else:
            return None

    def get_template_names(self):
        template_names = super(DetailView, self).get_template_names()
        if self.object and self.object.template:
            template_names = ['js_events/' + self.object.template] + template_names
        return self.prefix_template_names(template_names)


class EventListBase(AppConfigMixin, AppHookCheckMixin, TemplatePrefixMixin,
                    PreviewModeMixin, ViewUrlMixin, ListView):
    model = Event
    show_header = False

    def get_strict(self):
        return False

    def get(self, request, *args, **kwargs):
        self.edit_mode = (request.toolbar and request.toolbar.edit_mode_active)
        self.filterset = EventFilters(self.request.GET or DEFAULT_FILTERS, queryset=self.get_queryset())
        if not self.filterset.is_bound or self.filterset.is_valid() or not self.get_strict():
            self.object_list = self.filterset.qs.distinct()
        else:
            self.object_list = self.filterset.queryset.none()
        context = self.get_context_data(filter=self.filterset,
                                        object_list=self.object_list)
        return self.render_to_response(context)

    def get_paginate_by(self, queryset):
        if self.paginate_by is not None:
            return self.paginate_by
        else:
            try:
                return self.config.paginate_by
            except AttributeError:
                return 10  # sensible failsafe

    def get_pagination_options(self):
        # Django does not handle negative numbers well
        # when using variables.
        # So we perform the conversion here.
        if self.config:
            options = {
                'pages_start': self.config.pagination_pages_start,
                'pages_visible': self.config.pagination_pages_visible,
            }
        else:
            options = {
                'pages_start': 10,
                'pages_visible': 4,
            }

        pages_visible_negative = -options['pages_visible']
        options['pages_visible_negative'] = pages_visible_negative
        options['pages_visible_total'] = options['pages_visible'] + 1
        options['pages_visible_total_negative'] = pages_visible_negative - 1
        return options

    def get_context_data(self, **kwargs):
        context = super(EventListBase, self).get_context_data(**kwargs)
        context['pagination'] = self.get_pagination_options()
        return context


class EventList(CustomListMixin, EventListBase):
    """A complete list of events."""
    show_header = True

    def get_queryset(self):
        qs = super(EventList, self).get_queryset()
        # exclude featured events from queryset, to allow featured event
        # plugin on the list view page without duplicate entries in page qs.
        exclude_count = self.config.exclude_featured
        if exclude_count:
            featured_qs = Event.objects.all().filter(is_featured=True)
            if not self.edit_mode:
                featured_qs = featured_qs.published()
            exclude_featured = featured_qs[:exclude_count].values_list('pk')
            qs = qs.exclude(pk__in=exclude_featured)
        return qs


class EventSearchResultsList(EventListBase):
    model = Event
    http_method_names = ['get', 'post', ]
    partial_name = 'js_events/includes/search_results.html'
    template_name = 'js_events/event_list.html'

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get('q')
        self.max_events = request.GET.get('max_events', 0)
        self.edit_mode = (request.toolbar and request.toolbar.edit_mode_active)
        return super(EventSearchResultsList, self).get(request)

    def get_paginate_by(self, queryset):
        """
        If a max_events was set (by a plugin), use that figure, else,
        paginate by the app_config's settings.
        """
        return self.max_events or super(
            EventSearchResultsList, self).get_paginate_by(self.get_queryset())

    def get_queryset(self):
        qs = super(EventSearchResultsList, self).get_queryset()
        if not self.edit_mode:
            qs = qs.published()
        if self.query:
            return qs.filter(
                Q(translations__title__icontains=self.query) |
                Q(translations__lead_in__icontains=self.query) |
                Q(translations__search_data__icontains=self.query)
            ).distinct()
        else:
            return qs.none()

    def get_context_data(self, **kwargs):
        cxt = super(EventSearchResultsList, self).get_context_data(**kwargs)
        cxt['query'] = self.query
        return cxt

    def get_template_names(self):
        if self.request.is_ajax:
            template_names = [self.partial_name]
        else:
            template_names = [self.template_name]
        return self.prefix_template_names(template_names)


class CategoryEventList(EventListBase):
    """A list of events filtered by categories."""
    def get_queryset(self):
        return super(CategoryEventList, self).get_queryset().filter(
            categories=self.category
        )

    def get(self, request, category):
        self.category = get_object_or_404(
            Category, translations__slug=category)
        return super(CategoryEventList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['event_category'] = self.category
        ctx = super(CategoryEventList, self).get_context_data(**kwargs)
        ctx['event_category'] = self.category
        return ctx


class DateRangeEventList(EventListBase):
    """A list of events for a specific date range"""
    def get_queryset(self):
        return super(DateRangeEventList, self).get_queryset().filter(
            publishing_date__gte=self.date_from,
            publishing_date__lt=self.date_to
        )

    def _daterange_from_kwargs(self, kwargs):
        raise NotImplemented('Subclasses of DateRangeEventList need to'
                             'implement `_daterange_from_kwargs`.')

    def get(self, request, **kwargs):
        self.date_from, self.date_to = self._daterange_from_kwargs(kwargs)
        return super(DateRangeEventList, self).get(request)

    def get_context_data(self, **kwargs):
        kwargs['event_day'] = (
            int(self.kwargs.get('day')) if 'day' in self.kwargs else None)
        kwargs['event_month'] = (
            int(self.kwargs.get('month')) if 'month' in self.kwargs else None)
        kwargs['event_year'] = (
            int(self.kwargs.get('year')) if 'year' in self.kwargs else None)
        if kwargs['event_year']:
            kwargs['event_archive_date'] = date(
                kwargs['event_year'],
                kwargs['event_month'] or 1,
                kwargs['event_day'] or 1)
        return super(DateRangeEventList, self).get_context_data(**kwargs)


class YearEventList(DateRangeEventList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), 1, 1)
        date_to = date_from + relativedelta(years=1)
        return date_from, date_to


class MonthEventList(DateRangeEventList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), int(kwargs['month']), 1)
        date_to = date_from + relativedelta(months=1)
        return date_from, date_to


class DayEventList(DateRangeEventList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(
            int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        date_to = date_from + relativedelta(days=1)
        return date_from, date_to


class EventsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Event.objects.published()

    def lastmod(self, obj):
        return obj.publishing_date  # MOD date exists?  (e.g. when plugins are updated)
