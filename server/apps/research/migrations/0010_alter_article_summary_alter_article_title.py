# Generated by Django 5.0.8 on 2024-08-21 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0009_alter_article_thumb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='summary',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=500),
        ),
    ]