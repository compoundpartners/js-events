# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from .models import JSEvents


@plugin_pool.register_plugin
class JSEventsPlugin(CMSPluginBase):
    model = JSEvents
    name = _('Jumpsuite Events')
    admin_preview = False
    render_template = 'js_events/js_events.html'

    def render(self, context, instance, placeholder):
        context.update({
            'object': instance,
            'placeholder': placeholder,
        })
        return context
