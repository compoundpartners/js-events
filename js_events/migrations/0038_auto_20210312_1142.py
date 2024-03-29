# Generated by Django 2.2.19 on 2021-03-12 11:42

import aldryn_translation_tools.models
from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('js_events', '0037_event_share_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Channel',
                'verbose_name_plural': 'Channels',
                'ordering': ['position'],
            },
            bases=(aldryn_translation_tools.models.TranslatedAutoSlugifyMixin, aldryn_translation_tools.models.TranslationHelperMixin, parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='event',
            name='channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='js_events.Channel', verbose_name='channel'),
        ),
        migrations.CreateModel(
            name='ChannelTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=234, verbose_name='name')),
                ('slug', models.SlugField(blank=True, help_text='Used in the URL. If changed, the URL will change. Clear it to have it re-created automatically.', max_length=255, verbose_name='slug')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='js_events.Channel')),
            ],
            options={
                'verbose_name': 'Channel Translation',
                'db_table': 'js_events_channel_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
