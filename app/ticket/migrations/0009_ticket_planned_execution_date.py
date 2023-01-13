# Generated by Django 4.1.4 on 2023-01-10 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0008_ticket_metadata"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="planned_execution_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="Плановую дата выезда/исполнения"
            ),
        ),
    ]