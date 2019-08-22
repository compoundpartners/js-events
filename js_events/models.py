# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import six

from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_categories.models import Category
from aldryn_categories.fields import CategoryManyToManyField
from aldryn_translation_tools.models import TranslatedAutoSlugifyMixin, TranslationHelperMixin
from aldryn_people.models import Person
from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language, get_redirect_on_fallback
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import connection, models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override, ugettext
from djangocms_text_ckeditor.fields import HTMLField
from sortedm2m.fields import SortedManyToManyField
from filer.fields.image import FilerImageField
from djangocms_icon.fields import Icon
from parler.models import TranslatableModel, TranslatedFields
from aldryn_newsblog.utils import get_plugin_index_data, get_request, strip_tags
from aldryn_people.vcard import Vcard
from .cms_appconfig import EventsConfig
from .managers import RelatedManager, SpeakerManager

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse


@python_2_unicode_compatible
class Event(TranslatedAutoSlugifyMixin,
              TranslationHelperMixin,
              TranslatableModel):

    # TranslatedAutoSlugifyMixin options
    slug_source_field_name = 'title'
    slug_default = _('untitled-event')
    # when True, updates the event's search_data field
    # whenever the event is saved or a plugin is saved
    # on the event's content placeholder.
    update_search_on_save = getattr(
        settings,
        'EVENTS_UPDATE_SEARCH_DATA_ON_SAVE',
        False
    )

    translations = TranslatedFields(
        title=models.CharField(_('title'), max_length=234),
        slug=models.SlugField(
            verbose_name=_('slug'),
            max_length=255,
            db_index=True,
            blank=True,
            help_text=_(
                'Used in the URL. If changed, the URL will change. '
                'Clear it to have it re-created automatically.'),
        ),
        lead_in=HTMLField(
            verbose_name=_('Summary'), default='',
            help_text=_(
                'The Summary gives the reader the main idea of the story, this '
                'is useful in overviews, lists or as an introduction to your '
                'event.'
            ),
            blank=True,
        ),
        location=HTMLField(
            verbose_name=_('Location'), default='',
            blank=True,
        ),
        display_location=models.CharField(_('Display Location'), max_length=255,
            null=True,  blank=True,
        ),
        meta_title=models.CharField(
            max_length=255, verbose_name=_('meta title'),
            blank=True, default=''),
        meta_description=models.TextField(
            verbose_name=_('meta description'), blank=True, default=''),
        meta_keywords=models.TextField(
            verbose_name=_('meta keywords'), blank=True, default=''),
        meta={'unique_together': (('language_code', 'slug', ), )},

        search_data=models.TextField(blank=True, editable=False)
    )

    price=models.CharField(
        max_length=255,
        verbose_name=_('Event Price'),
        blank=True,
        default='')
    cpd_points=models.CharField(
        max_length=255,
        verbose_name=_('CPD Points'),
        blank=True,
        default='')
    event_start = models.DateTimeField(_('Event start'), default=now)
    event_end = models.DateTimeField(_('Event end'), null=True, blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=5,
        verbose_name=_('Event latitude'), blank=True, null=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5,
        verbose_name=_('Event longitude'), blank=True, null=True)
    host = models.ForeignKey(Person, null=True, blank=True,
        verbose_name=_('host'))
    host_2 = models.ForeignKey(Person, related_name='host_2', null=True, blank=True,
        verbose_name=_('second host'))
    host_3 = models.ForeignKey(Person, related_name='host_3', null=True, blank=True,
        verbose_name=_('third host'))
    registration_until = models.DateTimeField(_('Allow registration until'),
        blank=True, null=True)
    registration_content = PlaceholderField('Hide After Happened',
                               related_name='events_event_registration_content')
    sidebar = PlaceholderField('Event Sidebar',
                               related_name='events_event_sidebar')
    registration_link = models.CharField(max_length=255,
        verbose_name=_('Registration link'),
        blank=True, default='',
        help_text=_('link to an external registration system'),
    )
    external_link = models.CharField(max_length=255,
        verbose_name=_('External link'),
        blank=True, default='',
        help_text=_('link to an external registration system'),
    )
    link_text = models.CharField(max_length=255,
        verbose_name=_('Link Text'),
        blank=True, default='',
        help_text=_('Text to appear on either the Registration Link or External Link'),
    )
    redirect_url = models.CharField(max_length=255,
        verbose_name=_('Redirect URL'),
        blank=True, default='',
        help_text=_('when this value is filled in the Event page does not load, it redirects to the entered url'),
    )

    content = PlaceholderField('Event Content',
                               related_name='events_event_content')
    app_config = AppHookConfigField(
        EventsConfig,
        verbose_name=_('Section'),
        help_text='',
    )
    categories = CategoryManyToManyField(Category,
                                         verbose_name=_('categories'),
                                         blank=True)
    publishing_date = models.DateTimeField(_('publishing date'),
                                           default=now)
    is_published = models.BooleanField(_('is published'), default=False,
                                       db_index=True)
    is_featured = models.BooleanField(_('is featured'), default=False,
                                      db_index=True)
    hero_event = models.BooleanField(_('Hero Event'), default=False,
                                      db_index=True)
    featured_image = FilerImageField(
        verbose_name=_('featured image'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    show_on_sitemap = models.BooleanField(_('Show on sitemap'), null=False, default=True)
    show_on_xml_sitemap = models.BooleanField(_('Show on xml sitemap'), null=False, default=True)
    noindex = models.BooleanField(_('noindex'), null=False, default=False)
    nofollow = models.BooleanField(_('nofollow'), null=False, default=False)

    # Setting "symmetrical" to False since it's a bit unexpected that if you
    # set "B relates to A" you immediately have also "A relates to B". It have
    # to be forced to False because by default it's True if rel.to is "self":
    #
    # https://github.com/django/django/blob/1.8.4/django/db/models/fields/related.py#L2144
    #
    # which in the end causes to add reversed releted-to entry as well:
    #
    # https://github.com/django/django/blob/1.8.4/django/db/models/fields/related.py#L977
    services = SortedManyToManyField('js_services.Service',
        verbose_name=_('services'), blank=True)
    locations = SortedManyToManyField('js_locations.location',
        verbose_name=_('locations'), blank=True)

    objects = RelatedManager()

    class Meta:
        ordering = ['-event_start']

    def get_class(self):
        '''Return class name'''
        return self.__class__.__name__

    @property
    def type(self):
        '''Event Type / Section.'''
        return self.app_config

    @property
    def type_slug(self):
        '''Event Type / Section Machine Name'''
        return self.app_config.namespace

    @property
    def published(self):
        """
        Returns True only if the event (is_published == True) AND has a
        published_date that has passed.
        """
        return (self.is_published and self.publishing_date <= now())

    @property
    def future(self):
        """
        Returns True if the event is published but is scheduled for a
        future date/time.
        """
        return (self.is_published and self.publishing_date > now())

    @property
    def show_registration_content(self):
        return (self.registration_until or self.event_start) > now()

    @property
    def start_date(self):
        return self.event_start.date()

    @property
    def start_time(self):
        return self.event_start.time()

    @property
    def end_date(self):
        return self.event_end.date()

    @property
    def end_time(self):
        return self.event_end.time()

    def get_absolute_url(self, language=None):
        """Returns the url for this Event in the selected permalink format."""
        if not language:
            language = get_current_language()
        kwargs = {}
        permalink_type = self.app_config.permalink_type
        if 'y' in permalink_type:
            kwargs.update(year=self.publishing_date.year)
        if 'm' in permalink_type:
            kwargs.update(month="%02d" % self.publishing_date.month)
        if 'd' in permalink_type:
            kwargs.update(day="%02d" % self.publishing_date.day)
        if 'i' in permalink_type:
            kwargs.update(pk=self.pk)
        if 's' in permalink_type:
            slug, lang = self.known_translation_getter(
                'slug', default=None, language_code=language)
            if slug and lang:
                site_id = getattr(settings, 'SITE_ID', None)
                if get_redirect_on_fallback(language, site_id):
                    language = lang
                kwargs.update(slug=slug)

        if self.app_config and self.app_config.namespace:
            namespace = '{0}:'.format(self.app_config.namespace)
        else:
            namespace = ''

        with override(language):
            return reverse('{0}event-detail'.format(namespace), kwargs=kwargs)

    def get_search_data(self, language=None, request=None):
        """
        Provides an index for use with Haystack, or, for populating
        Event.translations.search_data.
        """
        if not self.pk:
            return ''
        if language is None:
            language = get_current_language()
        if request is None:
            request = get_request(language=language)
        title = self.safe_translation_getter('title', '')
        description = self.safe_translation_getter('lead_in', '')
        location = self.safe_translation_getter('location', '')
        text_bits = [title, strip_tags(description), strip_tags(location)]
        for category in self.categories.all():
            text_bits.append(
                force_unicode(category.safe_translation_getter('name')))
        for service in self.services.all():
            text_bits.append(
                force_unicode(service.safe_translation_getter('title')))
        if self.content:
            plugins = self.content.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                plugin_text_content = ' '.join(
                    get_plugin_index_data(base_plugin, request))
                text_bits.append(plugin_text_content)
        return ' '.join(text_bits)

    def save(self, *args, **kwargs):
        # Update the search index
        if self.update_search_on_save:
            self.search_data = self.get_search_data()

        # slug would be generated by TranslatedAutoSlugifyMixin
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True)


@python_2_unicode_compatible
class Speaker(models.Model):
    first_name = models.CharField(
        _('first name'), max_length=255, blank=False,
        default='', help_text=_("Provide this speaker's first name."))
    last_name = models.CharField(
        _('last name'), max_length=255, blank=False,
        default='', help_text=_("Provide this speaker's last name."))
    suffix = models.CharField(
        _('suffix'), max_length=60, blank=True,
        default='', help_text=_("Provide this speaker's suffix."))
    slug = models.SlugField(
        _('unique slug'), max_length=255, blank=True,
        default='',
        help_text=_("Leave blank to auto-generate a unique slug."))
    company = models.CharField(
        _('company'), max_length=255, blank=True,
        default='', help_text=_("Provide this speaker's company."))
    link = models.URLField(
        verbose_name=_('link'), null=True, blank=True)

    description = HTMLField(_('description'), blank=True, default='')
    function = models.CharField(_('role'), max_length=255, blank=True, default='')
    is_published = models.BooleanField(
        verbose_name=_('show on website'), default=True)
    visual = FilerImageField(
        null=True, blank=True, default=None, on_delete=models.SET_NULL)
    email = models.EmailField(
        verbose_name=_("email"), blank=True, default='')
    mobile = models.CharField(
        verbose_name=_('mobile'), null=True, blank=True, max_length=100)
    phone = models.CharField(
        verbose_name=_('phone'), null=True, blank=True, max_length=100)
    second_phone = models.CharField(
        verbose_name=_('secondary phone'), null=True, blank=True, max_length=100)
    fax = models.CharField(
        verbose_name=_('fax'), null=True, blank=True, max_length=100)
    facebook = models.URLField(
        verbose_name=_('facebook'), null=True, blank=True, max_length=200)
    twitter = models.CharField(
        verbose_name=_('twitter'), null=True, blank=True, max_length=100)
    linkedin = models.URLField(
        verbose_name=_('linkedin'), null=True, blank=True, max_length=200)
    vcard_enabled = models.BooleanField(
        verbose_name=_('enable vCard download'), default=True)

    objects = SpeakerManager()

    class Meta:
        verbose_name = _('Speaker')
        verbose_name_plural = _('Speakers')

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def name(self):
        return self.__str__()

    def get_vcard_url(self, language=None):
        return 'vcard/%s/' % self.slug


    def get_vcard(self, request=None):
        vcard = Vcard()

        safe_name = self.name()
        vcard.add_line('FN', safe_name)
        vcard.add_line('N', [None, safe_name, None, None, None])

        if self.visual:
            ext = self.visual.extension.upper()
            try:
                with open(self.visual.path, 'rb') as f:
                    data = force_text(base64.b64encode(f.read()))
                    vcard.add_line('PHOTO', data, TYPE=ext, ENCODING='b')
            except IOError:
                if request:
                    url = urlparse.urljoin(request.build_absolute_uri(),
                                           self.visual.url),
                    vcard.add_line('PHOTO', url, TYPE=ext)

        if self.email:
            vcard.add_line('EMAIL', self.email)

        if self.function:
            vcard.add_line('TITLE', self.function)

        if self.phone:
            vcard.add_line('TEL', self.phone, TYPE='WORK')
        if self.mobile:
            vcard.add_line('TEL', self.mobile, TYPE='CELL')

        if self.fax:
            vcard.add_line('TEL', self.fax, TYPE='FAX')

        return six.b('{}'.format(vcard))


class PluginEditModeMixin(object):
    def get_edit_mode(self, request):
        """
        Returns True only if an operator is logged-into the CMS and is in
        edit mode.
        """
        return (
            hasattr(request, 'toolbar') and request.toolbar and
            request.toolbar.edit_mode)


class AdjustableCacheModelMixin(models.Model):
    # NOTE: This field shouldn't even be displayed in the plugin's change form
    # if using django CMS < 3.3.0
    cache_duration = models.PositiveSmallIntegerField(
        default=0,  # not the most sensible, but consistent with older versions
        blank=False,
        help_text=_(
            "The maximum duration (in seconds) that this plugin's content "
            "should be cached.")
    )

    class Meta:
        abstract = True


@python_2_unicode_compatible
class EventRelatedPlugin(PluginEditModeMixin, AdjustableCacheModelMixin,
                            CMSPlugin):
    # NOTE: This one does NOT subclass NewsBlogCMSPlugin. This is because this
    # plugin can really only be placed on the article detail view in an apphook.
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name='+', parent_link=True)

    title = models.CharField(max_length=255, blank=True, verbose_name=_('Title'))
    icon = Icon(blank=False, default='')
    image = FilerImageField(null=True, blank=True, related_name="related_events_title_image")
    number_of_items = models.PositiveSmallIntegerField(verbose_name=_('Number of events'))
    layout = models.CharField(max_length=30, verbose_name=_('layout'))
    time_period = models.CharField(max_length=30, verbose_name=_('Time Period'))
    featured = models.BooleanField(blank=True, default=False)
    exclude_current_item = models.BooleanField(blank=True, default=False, verbose_name=_('Exclude current event'))
    related_types = SortedManyToManyField(EventsConfig, verbose_name=_('related sections'), blank=True, symmetrical=False)
    related_categories = SortedManyToManyField(Category, verbose_name=_('related categories'), blank=True, symmetrical=False)
    related_services = SortedManyToManyField('js_services.Service', verbose_name=_('related services'), blank=True, symmetrical=False)
    related_hosts = SortedManyToManyField(Person, verbose_name=_('related hosts'), blank=True, symmetrical=False)
    related_locations = SortedManyToManyField('js_locations.location', verbose_name=_('related locations'), blank=True)

    more_button_is_shown = models.BooleanField(blank=True, default=False, verbose_name=_('Show “See More Button”'))
    more_button_text = models.CharField(max_length=255, blank=True, verbose_name=_('See More Button Text'))
    more_button_link = models.CharField(max_length=255, blank=True, verbose_name=_('See More Button Link'))

    def copy_relations(self, oldinstance):
        self.related_types = oldinstance.related_types.all()
        self.related_categories = oldinstance.related_categories.all()
        self.related_services = oldinstance.related_services.all()
        self.related_hosts = oldinstance.related_hosts.all()
        self.related_locations = oldinstance.related_locations.all()

    def __str__(self):
        return ugettext('Related events')


@receiver(post_save, dispatch_uid='event_update_search_data')
def update_search_data(sender, instance, **kwargs):
    """
    Upon detecting changes in a plugin used in an event's content
    (PlaceholderField), update the event's search_index so that we can
    perform simple searches even without Haystack, etc.
    """
    is_cms_plugin = issubclass(instance.__class__, CMSPlugin)

    if Event.update_search_on_save and is_cms_plugin:
        placeholder = (getattr(instance, '_placeholder_cache', None) or
                       instance.placeholder)
        if hasattr(placeholder, '_attached_model_cache'):
            if placeholder._attached_model_cache == Event and placeholder.slot == 'content':
                event = placeholder._attached_model_cache.objects.language(
                    instance.language).get(content=placeholder.pk)
                event.search_data = event.get_search_data(instance.language)
                event.save()
