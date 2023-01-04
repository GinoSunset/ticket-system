# Generated by Django 4.1.4 on 2023-01-04 16:45

from django.db import migrations, models
import django.utils.timezone
import ticket.models


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0005_comment_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="date_create",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="comment",
            name="date_update",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="comment",
            name="file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=ticket.models.ticket_directory_path,
                verbose_name="Файл",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="text",
            field=models.TextField(
                blank=True, null=True, verbose_name="Текст комментария"
            ),
        ),
    ]
