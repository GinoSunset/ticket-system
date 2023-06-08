# Generated by Django 4.1.4 on 2023-06-08 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("manufactures", "0007_remove_manufacture_count_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="nomenclature",
            name="bd_count",
            field=models.IntegerField(default=1, verbose_name="Количество БД"),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="bd_type",
            field=models.CharField(
                choices=[("IN", "Внутренний"), ("OU", "Внешний")],
                default="IN",
                max_length=2,
                verbose_name="Тип БД",
            ),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="body",
            field=models.CharField(
                choices=[("PL", "Плекс"), ("PR", "Профиль"), ("S", "S")],
                default="PL",
                max_length=2,
                verbose_name="Корпус",
            ),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="frame_type",
            field=models.CharField(
                choices=[("AM", "AM"), ("RF", "РЧ")],
                default="AM",
                max_length=2,
                verbose_name="Тип",
            ),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="illumination",
            field=models.BooleanField(default=False, verbose_name="Подсветка"),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="md",
            field=models.BooleanField(default=False, verbose_name="MD"),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="mdg",
            field=models.BooleanField(default=False, verbose_name="MDG"),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="rx_count",
            field=models.IntegerField(default=1, verbose_name="Количество RX"),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="tx_count",
            field=models.IntegerField(default=1, verbose_name="Количество TX"),
        ),
        migrations.AddField(
            model_name="nomenclature",
            name="wifi",
            field=models.BooleanField(default=False, verbose_name="Wifi"),
        ),
    ]
