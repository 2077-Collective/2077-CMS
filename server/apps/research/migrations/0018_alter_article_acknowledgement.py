# Generated by Django 5.0.8 on 2024-08-29 07:19

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0017_remove_article_time_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='acknowledgement',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]