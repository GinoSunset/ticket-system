# Generated by Django 4.1.4 on 2023-01-09 14:45

from django.db import migrations, models
import django.db.models.deletion
import ticket.models


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0006_comment_date_create_comment_date_update_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="file",
        ),
        migrations.CreateModel(
            name="CommentFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=ticket.models.ticket_directory_path,
                        verbose_name="Файл",
                    ),
                ),
                (
                    "comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="files",
                        to="ticket.comment",
                    ),
                ),
            ],
        ),
    ]
