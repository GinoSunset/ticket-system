# Generated by Django 4.1.4 on 2023-09-04 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0016_nomenclature_amperage_3_2_nomenclature_amperage_6"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nomenclature",
            name="bp_type",
            field=models.CharField(
                choices=[("OU", "Внешний"), ("IN", "Внутренний")],
                default="IN",
                max_length=2,
                verbose_name="Тип БП",
            ),
        ),
        migrations.AlterField(
            model_name="nomenclature",
            name="illumination",
            field=models.BooleanField(default=True, verbose_name="Подсветка"),
        ),
    ]
