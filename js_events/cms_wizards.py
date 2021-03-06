# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
try:
    from django.core.urlresolvers import reverse, NoReverseMatch
except ImportError:
    # Django 2.0
    from django.urls import reverse, NoReverseMatch

from cms.api import add_plugin
from cms.utils import permissions
from cms.wizards.wizard_pool import wizard_pool
from cms.wizards.wizard_base import Wizard
from cms.wizards.forms import BaseFormMixin

from djangocms_text_ckeditor.widgets import TextEditorWidget
from djangocms_text_ckeditor.html import clean_html
from parler.forms import TranslatableModelForm

from .cms_appconfig import EventsConfig
from .models import Event

def is_valid_namespace(namespace):
    """
    Check if provided namespace has an app-hooked page.
    Returns True or False.
    """
    try:
        reverse('{0}:event-list'.format(namespace))
    except NoReverseMatch:
        return False
    return True

def get_published_app_configs():
    """
    Returns a list of app_configs that are attached to a published page.
    """
    published_configs = []
    for config in EventsConfig.objects.iterator():
        # We don't want to let people try to create Events here, as
        # they'll just 404 on arrival because the apphook isn't active.
        if is_valid_namespace(config.namespace):
            published_configs.append(config)
    return published_configs


class EventsEventWizard(Wizard):

    def user_has_add_permission(self, user, **kwargs):
        """
        Return True if the current user has permission to add an event.
        :param user: The current user
        :param kwargs: Ignored here
        :return: True if user has add permission, else False
        """
        # No one can create an Event, if there is no app_config yet.
        num_configs = get_published_app_configs()
        if not num_configs:
            return False

        # Ensure user has permission to create events.
        if user.is_superuser or user.has_perm("js_events.add_event"):
            return True

        # By default, no permission.
        return False


class CreateEventsEventForm(BaseFormMixin, TranslatableModelForm):
    """
    The ModelForm for the Events event wizard. Note that Event has a
    number of translated fields that we need to access, so, we use
    TranslatableModelForm
    """

    content = forms.CharField(
        label=_('Content'),
        required=False,
        widget=TextEditorWidget,
        help_text=_(
            "Optional. If provided, it will be added to the main body of "
            "the event as a text plugin, that can be formatted."
        )
    )

    class Meta:
        model = Event
        fields = ['title', 'app_config']
        # The natural widget for app_config is meant for normal Admin views and
        # contains JS to refresh the page on change. This is not wanted here.
        widgets = {'app_config': forms.Select()}

    def __init__(self, **kwargs):
        super(CreateEventsEventForm, self).__init__(**kwargs)

        # If there's only 1 (or zero) app_configs, don't bother show the
        # app_config choice field, we'll choose the option for the user.
        app_configs = get_published_app_configs()
        if len(app_configs) < 2:
            self.fields['app_config'].widget = forms.HiddenInput()
            self.fields['app_config'].initial = app_configs[0].pk

    def save(self, commit=True):
        event = super(CreateEventsEventForm, self).save(commit=False)
        #event.owner = self.user
        event.save()

        # If 'content' field has value, create a TextPlugin with same and add it to the PlaceholderField
        content = clean_html(self.cleaned_data.get('content', ''), False)
        if content and permissions.has_plugin_permission(self.user, 'TextPlugin', 'add'):
            add_plugin(
                placeholder=event.content,
                plugin_type='TextPlugin',
                language=self.language_code,
                body=content,
            )

        return event


events_event_wizard = EventsEventWizard(
    title=_(u"New event"),
    weight=200,
    form=CreateEventsEventForm,
    description=_(u"Create a event.")
)

wizard_pool.register(events_event_wizard)
