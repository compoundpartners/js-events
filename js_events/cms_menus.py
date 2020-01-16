# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from django.core.urlresolvers import NoReverseMatch
except ImportError:
    # Django 2.0
    from django.urls import NoReverseMatch
from django.utils.translation import (
    get_language_from_request,
    ugettext_lazy as _,
)

from cms.menu_bases import CMSAttachMenu
from cms.apphook_pool import apphook_pool
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import Event


class EventsMenu(CMSAttachMenu):
    name = _('Events Menu')

    def get_queryset(self, request):
        """Returns base queryset with support for preview-mode."""
        queryset = Event.objects
        if not (request.toolbar and request.toolbar.edit_mode):
            queryset = queryset.published()
        return queryset

    def get_nodes(self, request):
        nodes = []
        language = get_language_from_request(request, check_path=True)
        events = self.get_queryset(request).active_translations(language)

        if hasattr(self, 'instance') and self.instance:
            app = apphook_pool.get_apphook(self.instance.application_urls)
            config = app.get_config(self.instance.application_namespace)
            if config:
                events = events.filter(app_config=config)

        for event in events:
            try:
                url = event.get_absolute_url(language=language)
            except NoReverseMatch:
                url = None

            if url:
                node = NavigationNode(event.safe_translation_getter(
                    'title', language_code=language), url, event.pk)
                nodes.append(node)
        return nodes


menu_pool.register_menu(EventsMenu)
