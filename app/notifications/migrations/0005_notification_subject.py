# Generated by Django 4.1.4 on 2023-03-09 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0004_notification_type_notify"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="subject",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
