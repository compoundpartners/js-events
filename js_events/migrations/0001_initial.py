# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-12 16:25
from __future__ import unicode_literals

import aldryn_apphooks_config.fields
import aldryn_categories.fields
import aldryn_translation_tools.models
import app_data.fields
import cms.models.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import djangocms_text_ckeditor.fields
import filer.fields.image
import parler.models
import sortedm2m.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aldryn_categories', '0007_categorytranslation_landing_page'),
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('aldryn_people', '0026_person_services'),
        ('cms', '0020_old_tree_cleanup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True, verbose_name='Event latitude')),
                ('longitude', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True, verbose_name='Event longitude')),
                ('start_date', models.DateField(verbose_name='Sart date')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Sart time')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End date')),
                ('end_time', models.TimeField(blank=True, null=True, verbose_name='Sart time')),
                ('registration_until', models.DateTimeField(blank=True, null=True, verbose_name='Allow registration until')),
                ('registration_link', models.CharField(blank=True, default='', help_text='link to an external registration system', max_length=255, verbose_name='Registration link')),
                ('external_link', models.CharField(blank=True, default='', help_text='link to an external registration system', max_length=255, verbose_name='External link')),
                ('publishing_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='publishing date')),
                ('is_published', models.BooleanField(db_index=True, default=False, verbose_name='is published')),
                ('is_featured', models.BooleanField(db_index=True, default=False, verbose_name='is featured')),
            ],
            options={
                'ordering': ['-publishing_date'],
            },
            bases=(aldryn_translation_tools.models.TranslatedAutoSlugifyMixin, aldryn_translation_tools.models.TranslationHelperMixin, parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EventsConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100, verbose_name='Type')),
                ('namespace', models.CharField(default=None, max_length=100, unique=True, verbose_name='Instance namespace')),
                ('app_data', app_data.fields.AppDataField(default='{}', editable=False)),
                ('permalink_type', models.CharField(choices=[('s', 'the-eagle-has-landed/'), ('ys', '1969/the-eagle-has-landed/'), ('yms', '1969/07/the-eagle-has-landed/'), ('ymds', '1969/07/16/the-eagle-has-landed/'), ('ymdi', '1969/07/16/11/')], default='slug', help_text='Choose the style of urls to use from the examples. (Note, all types are relative to apphook)', max_length=8, verbose_name='permalink type')),
                ('non_permalink_handling', models.SmallIntegerField(choices=[(200, 'Allow'), (302, 'Redirect to permalink (default)'), (301, 'Permanent redirect to permalink'), (404, 'Return 404: Not Found')], default=302, help_text='How to handle non-permalink urls?', verbose_name='non-permalink handling')),
                ('paginate_by', models.PositiveIntegerField(default=5, help_text='When paginating list views, how many events per page?', verbose_name='Paginate size')),
                ('pagination_pages_start', models.PositiveIntegerField(default=10, help_text='When paginating list views, after how many pages should we start grouping the page numbers.', verbose_name='Pagination pages start')),
                ('pagination_pages_visible', models.PositiveIntegerField(default=4, help_text='When grouping page numbers, this determines how many pages are visible on each side of the active page.', verbose_name='Pagination pages visible')),
                ('exclude_featured', models.PositiveSmallIntegerField(blank=True, default=0, help_text='If you are using the Featured events plugin on the event list view, you may prefer to exclude featured events from the event list itself to avoid duplicates. To do this, enter the same number here as in your Featured events plugin.', verbose_name='Excluded featured events count')),
                ('template_prefix', models.CharField(blank=True, max_length=20, null=True, verbose_name='Prefix for template dirs')),
                ('search_indexed', models.BooleanField(default=True, help_text='Include events in search indexes?', verbose_name='Include in search index?')),
            ],
            options={
                'verbose_name': 'Section',
                'verbose_name_plural': 'Sections',
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='EventsConfigTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('app_title', models.CharField(max_length=234, verbose_name='name')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='js_events.EventsConfig')),
            ],
            options={
                'verbose_name': 'Section Translation',
                'db_table': 'js_events_eventsconfig_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='EventTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=234, verbose_name='title')),
                ('slug', models.SlugField(blank=True, help_text='Used in the URL. If changed, the URL will change. Clear it to have it re-created automatically.', max_length=255, verbose_name='slug')),
                ('lead_in', djangocms_text_ckeditor.fields.HTMLField(blank=True, default='', help_text='The Summary gives the reader the main idea of the story, this is useful in overviews, lists or as an introduction to your event.', verbose_name='Summary')),
                ('location', djangocms_text_ckeditor.fields.HTMLField(blank=True, default='', verbose_name='Location')),
                ('meta_title', models.CharField(blank=True, default='', max_length=255, verbose_name='meta title')),
                ('meta_description', models.TextField(blank=True, default='', verbose_name='meta description')),
                ('meta_keywords', models.TextField(blank=True, default='', verbose_name='meta keywords')),
                ('search_data', models.TextField(blank=True, editable=False)),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='js_events.Event')),
            ],
            options={
                'verbose_name': 'event Translation',
                'db_table': 'js_events_event_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='event',
            name='app_config',
            field=aldryn_apphooks_config.fields.AppHookConfigField(help_text='When selecting a value, the form is reloaded to get the updated default', on_delete=django.db.models.deletion.CASCADE, to='js_events.EventsConfig', verbose_name='Section'),
        ),
        migrations.AddField(
            model_name='event',
            name='categories',
            field=aldryn_categories.fields.CategoryManyToManyField(blank=True, to='aldryn_categories.Category', verbose_name='categories'),
        ),
        migrations.AddField(
            model_name='event',
            name='content',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newsblog_event_content', slotname='newsblog_event_content', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='event',
            name='featured_image',
            field=filer.fields.image.FilerImageField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.FILER_IMAGE_MODEL, verbose_name='featured image'),
        ),
        migrations.AddField(
            model_name='event',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='aldryn_people.Person', verbose_name='host'),
        ),
        migrations.AddField(
            model_name='event',
            name='host_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host_2', to='aldryn_people.Person', verbose_name='second host'),
        ),
        migrations.AddField(
            model_name='event',
            name='host_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='host_3', to='aldryn_people.Person', verbose_name='third host'),
        ),
        migrations.AddField(
            model_name='event',
            name='related',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='js_events.Event', verbose_name='related events'),
        ),
        migrations.AlterUniqueTogether(
            name='eventtranslation',
            unique_together=set([('language_code', 'slug'), ('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='eventsconfigtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
