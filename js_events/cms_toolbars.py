# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.translation import (
    ugettext as _, get_language_from_request, override)

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool

from aldryn_apphooks_config.utils import get_app_instance
from aldryn_translation_tools.utils import (
    get_object_from_request,
    get_admin_url,
)

from .models import Event
from .cms_appconfig import EventsConfig

from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK


@toolbar_pool.register
class EventsToolbar(CMSToolbar):
    # watch_models must be a list, not a tuple
    # see https://github.com/divio/django-cms/issues/4135
    watch_models = [Event, ]
    supported_apps = ('js_events',)

    def get_on_delete_redirect_url(self, event, language):
        with override(language):
            url = reverse(
                '{0}:event-list'.format(event.app_config.namespace))
        return url

    def __get_events_config(self):
        try:
            __, config = get_app_instance(self.request)
            if not isinstance(config, EventsConfig):
                # This is not the app_hook you are looking for.
                return None
        except ImproperlyConfigured:
            # There is no app_hook at all.
            return None

        return config

    def populate(self):
        config = self.__get_events_config()
        if not config:
            # Do nothing if there is no events app_config to work with
            return

        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if user and view_name:
            language = get_language_from_request(self.request, check_path=True)


            # get existing admin menu
            admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)

            # add new Events item
            admin_menu.add_sideframe_item(_('Events'), url='/admin/js_events/event/', position=0)

            # If we're on an Event detail page, then get the event
            if view_name == '{0}:event-detail'.format(config.namespace):
                event = get_object_from_request(Event, self.request)
            else:
                event = None

            menu = self.toolbar.get_or_create_menu('events-app',
                                                   config.get_app_title())

            change_config_perm = user.has_perm(
                'js_events.change_eventsconfig')
            add_config_perm = user.has_perm(
                'js_events.add_eventsconfig')
            config_perms = [change_config_perm, add_config_perm]

            change_event_perm = user.has_perm(
                'js_events.change_event')
            delete_event_perm = user.has_perm(
                'js_events.delete_event')
            add_event_perm = user.has_perm('js_events.add_event')
            event_perms = [change_event_perm, add_event_perm,
                             delete_event_perm, ]

            if change_config_perm:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('js_events_eventsconfig_change',
                                    [config.pk, ], **url_args)
                menu.add_modal_item(_('Configure addon'), url=url)

            if any(config_perms) and any(event_perms):
                menu.add_break()

            if change_event_perm:
                url_args = {}
                if config:
                    url_args = {'app_config__id__exact': config.pk}
                url = get_admin_url('js_events_event_changelist',
                                    **url_args)
                menu.add_sideframe_item(_('Event list'), url=url)

            if add_event_perm:
                url_args = {'app_config': config.pk, 'owner': user.pk, }
                if language:
                    url_args.update({'language': language, })
                url = get_admin_url('js_events_event_add', **url_args)
                menu.add_modal_item(_('Add new event'), url=url)

            if change_event_perm and event:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('js_events_event_change',
                                    [event.pk, ], **url_args)
                menu.add_modal_item(_('Edit this event'), url=url,
                                    active=True)

            if delete_event_perm and event:
                redirect_url = self.get_on_delete_redirect_url(
                    event, language=language)
                url = get_admin_url('js_events_event_delete',
                                    [event.pk, ])
                menu.add_modal_item(_('Delete this event'), url=url,
                                    on_close=redirect_url)
