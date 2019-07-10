# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_translation_tools.sitemaps import I18NSitemap

from .models import Event
from .constants import SITEMAP_CHANGEFREQ, SITEMAP_PRIORITY


class EventsSitemap(I18NSitemap):

    changefreq = SITEMAP_CHANGEFREQ
    priority = SITEMAP_PRIORITY

    def __init__(self, *args, **kwargs):
        self.namespace = kwargs.pop('namespace', None)
        self.sitemap_type = kwargs.pop('type', 'xml')
        super(EventsSitemap, self).__init__(*args, **kwargs)

    def items(self):
        qs = Event.objects.published()
        if self.language is not None:
            qs = qs.translated(self.language)
        if self.namespace is not None:
            qs = qs.filter(app_config__namespace=self.namespace)
        if self.sitemap_type == 'html':
            qs = qs.exclude(show_on_sitemap=False)
        elif self.sitemap_type == 'xml':
            qs = qs.exclude(show_on_xml_sitemap=False)
        return qs

    def lastmod(self, obj):
        return obj.publishing_date
