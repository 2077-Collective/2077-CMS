# Generated by Django 5.0.8 on 2024-08-22 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0012_alter_article_summary_alter_article_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='summary',
            field=models.TextField(blank=True),
        ),
    ]
