# Generated by Django 5.0.8 on 2024-09-23 11:35

import apps.research.models.article
import django.db.models.deletion
import tinymce.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('twitter_username', models.CharField(blank=True, max_length=100, null=True)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Authors',
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.TextField()),
                ('content', tinymce.models.HTMLField(blank=True, null=True)),
                ('summary', models.TextField(blank=True)),
                ('acknowledgement', tinymce.models.HTMLField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True)),
                ('thumb', models.ImageField(blank=True, default=apps.research.models.article.get_default_thumb, upload_to='images/')),
                ('views', models.PositiveBigIntegerField(default=0)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('ready', 'Ready')], db_index=True, default='draft', max_length=10)),
                ('scheduled_publish_time', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('authors', models.ManyToManyField(blank=True, related_name='articles', to='research.author')),
                ('categories', models.ManyToManyField(blank=True, related_name='articles', to='research.category')),
            ],
            options={
                'ordering': ('-scheduled_publish_time',),
            },
        ),
    ]
