# Generated by Django 4.1.4 on 2023-02-26 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0025_comment_is_for_report"),
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Act",
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
                    "date_create",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "file_doc_act",
                    models.FileField(
                        upload_to="secret/acts/%Y/%m/",
                        verbose_name="Акт выполненных работ",
                    ),
                ),
                (
                    "file_act_pdf",
                    models.FileField(
                        upload_to="secret/acts/%Y/%m/",
                        verbose_name="Акт выполненных работ PDF",
                    ),
                ),
                (
                    "ticket",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="act",
                        to="ticket.ticket",
                        verbose_name="Заявка",
                    ),
                ),
            ],
        ),
    ]