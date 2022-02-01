# Generated by Django 2.2.24 on 2022-02-01 15:19

import cms.models.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('js_events', '0039_eventrelatedplugin_related_service_sections'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='related_articles_placeholder',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events_event_related_articles_placeholder', slotname='Related Articles', to='cms.Placeholder'),
        ),
    ]