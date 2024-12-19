import apps.research.models.article
import cloudinary.models
import cloudinary.uploader
from django.db import migrations
from django.core.files.storage import default_storage
import os


def transfer_to_cloudinary(apps, schema_editor):
    Article = apps.get_model("research", "Article")

    for instance in Article.objects.all():
        if instance.thumb:
            try:
                if hasattr(instance.thumb, "public_id"):
                    continue

                if hasattr(instance.thumb, "url"):
                    file_path = instance.thumb.path

                    if default_storage.exists(file_path):
                        with open(file_path, "rb") as file:
                            upload_result = cloudinary.uploader.upload(
                                file, folder="coverImage", resource_type="image"
                            )

                        instance.thumb = upload_result["public_id"]
                        instance.save()

                        # delete the local file
                        # default_storage.delete(file_path)

            except Exception as e:
                print(f"Info for Article {instance.id}: {str(e)}")


def reverse_transfer(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("research", "0017_article_gpt_summary_alter_article_summary"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="thumb",
            field=cloudinary.models.CloudinaryField(
                blank=True,
                default=apps.research.models.article.get_default_thumb,
                max_length=255,
                verbose_name="image",
            ),
        ),
        migrations.RunPython(transfer_to_cloudinary, reverse_transfer),
    ]
