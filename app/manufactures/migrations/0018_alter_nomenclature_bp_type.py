# Generated by Django 4.1.4 on 2023-09-04 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0017_alter_nomenclature_bp_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nomenclature",
            name="bp_type",
            field=models.CharField(
                choices=[("OU", "Внешний"), ("IN", "Внутренний")],
                default="OU",
                max_length=2,
                verbose_name="Тип БП",
            ),
        ),
    ]
