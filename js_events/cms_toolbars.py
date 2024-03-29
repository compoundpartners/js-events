# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
try:
    from django.core.urlresolvers import reverse, NoReverseMatch
except ImportError:
    # Django 2.0
    from django.urls import reverse, NoReverseMatch
from django.utils.translation import (
    ugettext as _, get_language_from_request, override)

from cms.api import get_page_draft
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.i18n import get_language_tuple, get_language_dict
from cms.utils.urlutils import add_url_parameters, admin_reverse
from menus.utils import DefaultLanguageChanger

from aldryn_apphooks_config.utils import get_app_instance
from aldryn_translation_tools.utils import (
#    get_object_from_request,
    get_admin_url,
)
from parler.models import TranslatableModel

from .models import Event
from .cms_appconfig import EventsConfig

from cms.cms_toolbars import (
    ADMIN_MENU_IDENTIFIER,
    LANGUAGE_MENU_IDENTIFIER,
)

def get_object_from_request(model, request,
                            pk_url_kwarg='pk',
                            slug_url_kwarg='slug',
                            slug_field='slug'):
    """
    Given a model and the request, try to extract and return an object
    from an available 'pk' or 'slug', or return None.

    Note that no checking is done that the obj's kwargs really are for objects
    matching the provided model (how would it?) so use only where appropriate.
    """
    language = get_language_from_request(request, check_path=True)
    kwargs = request.resolver_match.kwargs
    mgr = model.all_objects
    if pk_url_kwarg in kwargs:
        return mgr.filter(pk=kwargs[pk_url_kwarg]).first()
    elif slug_url_kwarg in kwargs:
        # If the model is translatable, and the given slug is a translated
        # field, then find it the Parler way.
        filter_kwargs = {slug_field: kwargs[slug_url_kwarg]}
        try:
            translated_fields = model._parler_meta.get_translated_fields()
        except AttributeError:
            translated_fields = []
        if issubclass(model, TranslatableModel) and slug_url_kwarg in translated_fields:
            return mgr.active_translations(language, **filter_kwargs).first()
        else:
            # OK, do it the normal way.
            return mgr.filter(**filter_kwargs).first()
    else:
        return None


ADD_OBJ_LANGUAGE_BREAK = "Add object language Break"

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
        self.page = get_page_draft(self.request.current_page)
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
                obj = get_object_from_request(Event, self.request)
            else:
                obj = None

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

            if change_event_perm and obj:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('js_events_event_change',
                                    [obj.pk, ], **url_args)
                menu.add_modal_item(_('Edit this event'), url=url,
                                    active=True)

            if delete_event_perm and obj:
                redirect_url = self.get_on_delete_redirect_url(
                    obj, language=language)
                url = get_admin_url('js_events_event_delete',
                                    [obj.pk, ])
                menu.add_modal_item(_('Delete this event'), url=url,
                                    on_close=redirect_url)

        if settings.USE_I18N:# and not self._language_menu:
            if obj:
                self._language_menu = self.toolbar.get_or_create_menu(LANGUAGE_MENU_IDENTIFIER, _('Language'), position=-1)
                self._language_menu.items = []
                languages = get_language_dict(self.current_site.pk)
                page_languages = self.page.get_languages()
                remove = []

                for code, name in get_language_tuple():
                    if code in obj.get_available_languages():
                        remove.append((code, name))
                        try:
                            url = obj.get_absolute_url(code)
                        except NoReverseMatch:
                            url = None
                        if url and code in page_languages:
                            self._language_menu.add_link_item(name, url=url, active=self.current_lang == code)

                if self.toolbar.edit_mode_active:
                    add = [l for l in languages.items() if l not in remove]
                    copy = [(code, name) for code, name in languages.items() if code != self.current_lang and (code, name) in remove]

                    if (add or len(remove) > 1 or copy) and change_event_perm:
                        self._language_menu.add_break(ADD_OBJ_LANGUAGE_BREAK)

                        if add:
                            add_plugins_menu = self._language_menu.get_or_create_menu('{0}-add-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Add Translation'))
                            for code, name in add:
                                url_args = {}
                                url = '%s?language=%s' % (get_admin_url('js_events_event_change',
                                    [obj.pk], **url_args), code)
                                add_plugins_menu.add_modal_item(name, url=url)

                        if len(remove) > 1:
                            remove_plugins_menu = self._language_menu.get_or_create_menu('{0}-del-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Delete Translation'))
                            for code, name in remove:
                                url = get_admin_url('js_events_event_delete_translation', [obj.pk, code])
                                remove_plugins_menu.add_modal_item(name, url=url)

                        if copy:
                            copy_plugins_menu = self._language_menu.get_or_create_menu('{0}-copy-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Copy all plugins'))
                            title = _('from %s')
                            question = _('Are you sure you want to copy all plugins from %s?')
                            url = get_admin_url('js_events_event_copy_language', [obj.pk])
                            for code, name in copy:
                                copy_plugins_menu.add_ajax_item(
                                    title % name, action=url,
                                    data={'source_language': code, 'target_language': self.current_lang},
                                    question=question % name, on_success=self.toolbar.REFRESH_PAGE
                                )
