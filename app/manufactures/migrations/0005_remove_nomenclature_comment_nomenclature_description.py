# Generated by Django 4.1.4 on 2023-06-04 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0004_manufacture_nomenclatures"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="nomenclature",
            name="comment",
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Описание"),
        ),
    ]