# Generated by Django 4.1.4 on 2023-10-25 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0018_alter_nomenclature_bp_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="nomenclature",
            name="amperage_1",
            field=models.BooleanField(
                default=False, help_text="Amperage  for AM", verbose_name="1"
            ),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="amperage_2",
            field=models.BooleanField(
                default=False, help_text="Amperage  for AM", verbose_name="2"
            ),
        ),
    ]