# Generated by Django 4.1.4 on 2023-02-06 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_contractorprofile_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="contractorprofile",
            name="company",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Компания"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="telegram_id",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Telegram ID"
            ),
        ),
    ]
