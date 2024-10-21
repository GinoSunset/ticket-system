# Generated by Django 5.1 on 2024-10-21 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0028_ticket_link_to_source_ticket_source_ticket"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="link_to_source",
            field=models.URLField(
                blank=True,
                help_text="Если задача создана через itsm, ссылка добавиться автоматически",
                null=True,
                verbose_name="Ссылка на источник",
            ),
        ),
    ]