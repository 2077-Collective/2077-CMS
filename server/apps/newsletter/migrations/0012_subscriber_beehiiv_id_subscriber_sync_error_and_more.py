# Generated by Django 5.0.8 on 2025-01-15 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0011_alter_newsletter_scheduled_send_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='beehiiv_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='sync_error',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='synced_to_beehiiv',
            field=models.BooleanField(default=False),
        ),
    ]
