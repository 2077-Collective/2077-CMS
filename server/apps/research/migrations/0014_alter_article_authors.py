# Generated by Django 5.0.8 on 2024-12-02 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0013_alter_article_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(blank=True, related_name='articles', to='research.author'),
        ),
    ]
