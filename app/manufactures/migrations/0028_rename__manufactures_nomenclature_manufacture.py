# Generated by Django 4.1.4 on 2023-11-07 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0027_remove_manufacture_nomenclatures"),
    ]

    operations = [
        migrations.RenameField(
            model_name="nomenclature",
            old_name="_manufactures",
            new_name="manufacture",
        ),
    ]
