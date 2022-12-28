# Generated by Django 4.1.4 on 2022-12-28 17:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ticket", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="contractor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="contractor_user",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Исполнитель",
            ),
        ),
    ]
