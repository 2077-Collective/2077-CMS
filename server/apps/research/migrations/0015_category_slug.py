# Generated by Django 5.0.8 on 2024-12-09 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0014_alter_article_authors'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
