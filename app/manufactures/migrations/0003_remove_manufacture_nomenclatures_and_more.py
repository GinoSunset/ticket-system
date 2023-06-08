# Generated by Django 4.1.4 on 2023-06-03 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0002_alter_nomenclature_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="manufacture",
            name="nomenclatures",
        ),
        migrations.CreateModel(
            name="ManufactureNomenclature",
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
                ("quantity", models.IntegerField(default=1, verbose_name="Количество")),
                (
                    "comment",
                    models.TextField(blank=True, null=True, verbose_name="Комментарий"),
                ),
                (
                    "manufacture",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="manufacture_nomenclatures",
                        to="manufactures.manufacture",
                        verbose_name="Заявка на производство",
                    ),
                ),
                (
                    "nomenclature",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="manufacture_nomenclatures",
                        to="manufactures.nomenclature",
                        verbose_name="Номенклатура",
                    ),
                ),
            ],
        ),
    ]
