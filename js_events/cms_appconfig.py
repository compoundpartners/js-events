# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_apphooks_config.models import AppHookConfig
from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from cms.models.fields import PlaceholderField
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import override, ugettext_lazy as _
from cms.utils.i18n import get_current_language
from parler.models import TranslatableModel, TranslatedFields


PERMALINK_CHOICES = (
    ('s', _('the-eagle-has-landed/', )),
    ('ys', _('1969/the-eagle-has-landed/', )),
    ('yms', _('1969/07/the-eagle-has-landed/', )),
    ('ymds', _('1969/07/16/the-eagle-has-landed/', )),
    ('ymdi', _('1969/07/16/11/', )),
)

NON_PERMALINK_HANDLING = (
    (200, _('Allow')),
    (302, _('Redirect to permalink (default)')),
    (301, _('Permanent redirect to permalink')),
    (404, _('Return 404: Not Found')),
)

# TODO override default if support for Django 1.6 will be dropped
TEMPLATE_PREFIX_CHOICES = getattr(
    settings, 'EVENTS_TEMPLATE_PREFIXES', [])


@python_2_unicode_compatible
class EventsConfig(TranslatableModel, AppHookConfig):
    """Adds some translatable, per-app-instance fields."""
    translations = TranslatedFields(
        app_title=models.CharField(_('name'), max_length=234),
    )

    allow_post = models.BooleanField(
        _('Allow POST requests'),
        default=False,
    )
    permalink_type = models.CharField(
        _('permalink type'), max_length=8,
        blank=False, default='slug', choices=PERMALINK_CHOICES,
        help_text=_('Choose the style of urls to use from the examples. '
                    '(Note, all types are relative to apphook)'))

    non_permalink_handling = models.SmallIntegerField(
        _('non-permalink handling'),
        blank=False, default=302,
        choices=NON_PERMALINK_HANDLING,
        help_text=_('How to handle non-permalink urls?'))

    paginate_by = models.PositiveIntegerField(
        _('Paginate size'),
        blank=False,
        default=5,
        help_text=_('When paginating list views, how many events per page?'),
    )
    pagination_pages_start = models.PositiveIntegerField(
        _('Pagination pages start'),
        blank=False,
        default=10,
        help_text=_('When paginating list views, after how many pages '
                    'should we start grouping the page numbers.'),
    )
    pagination_pages_visible = models.PositiveIntegerField(
        _('Pagination pages visible'),
        blank=False,
        default=4,
        help_text=_('When grouping page numbers, this determines how many '
                    'pages are visible on each side of the active page.'),
    )
    exclude_featured = models.PositiveSmallIntegerField(
        _('Excluded featured events count'),
        blank=True,
        default=0,
        help_text=_(
            'If you are using the Featured events plugin on the event list '
            'view, you may prefer to exclude featured events from the '
            'event list itself to avoid duplicates. To do this, enter the '
            'same number here as in your Featured events plugin.'),
    )
    template_prefix = models.CharField(
        max_length=20,
        null=True, blank=True,
        choices=TEMPLATE_PREFIX_CHOICES,
        verbose_name=_("Prefix for template dirs"))

    # EVENTS_SEARCH
    search_indexed = models.BooleanField(
        _('Include in search index?'),
        default=True,
        help_text=_('Include events in search indexes?'),
    )

    def get_app_title(self):
        return getattr(self, 'app_title', _('untitled'))

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')

    def __str__(self):
        return self.safe_translation_getter('app_title')

    def get_absolute_url(self, language=None):
        if not language:
            language = get_current_language()
        with override(language):
            return reverse('{0}:event-list'.format(self.namespace))


class EventsConfigForm(AppDataForm):
    default_published = forms.BooleanField(
        label=_(u'Post published by default'), required=False,
        initial=getattr(settings, 'EVENTS_DEFAULT_PUBLISHED', False))


setup_config(EventsConfigForm, EventsConfig)
