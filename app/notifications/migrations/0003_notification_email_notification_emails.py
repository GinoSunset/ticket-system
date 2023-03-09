# Generated by Django 4.1.4 on 2023-03-07 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0002_alter_notification_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="emails",
            field=models.TextField(blank=True, null=True),
        ),
    ]
