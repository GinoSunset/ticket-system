# Generated by Django 4.1.4 on 2023-06-24 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0012_remove_nomenclature_bd_count_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="nomenclature",
            options={
                "ordering": ["date_create"],
                "verbose_name": "Номенклатура",
                "verbose_name_plural": "Номенклатуры",
            },
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="status",
            field=models.CharField(
                choices=[("NW", "Новый"), ("IP", "В работе"), ("RD", "Готово")],
                default="NW",
                max_length=2,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="nomenclature",
            name="wifi",
            field=models.BooleanField(default=False, verbose_name="Wi-Fi"),
        ),
    ]
