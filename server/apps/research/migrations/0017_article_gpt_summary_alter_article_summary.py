# Generated by Django 5.0.8 on 2024-12-10 18:18

import tinymce.models
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('research', '0016_alter_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='gpt_summary',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]
