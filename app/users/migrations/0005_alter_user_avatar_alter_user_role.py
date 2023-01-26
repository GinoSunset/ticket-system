# Generated by Django 4.1.4 on 2023-01-24 19:03

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_customerprofile_parser"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=users.models.avatar_directory_path,
                verbose_name="Аватар",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Администратор"),
                    ("OPERATOR", "Оператор"),
                    ("CUSTOMER", "Заказчик"),
                    ("CONTRACTOR", "Исполнитель"),
                    ("OTHER", "Не назначен"),
                ],
                max_length=50,
                verbose_name="Роль",
            ),
        ),
    ]