# Generated by Django 5.0.8 on 2024-10-23 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0006_article_is_sponsored_article_sponsor_color_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='sponsor_color',
            field=models.CharField(default='#FF0420 !important', max_length=7),
        ),
        migrations.AlterField(
            model_name='article',
            name='sponsor_text_color',
            field=models.CharField(default='#000000 !important', max_length=7),
        ),
    ]
