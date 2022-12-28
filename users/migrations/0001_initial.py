# Generated by Django 4.1.4 on 2022-12-28 16:49

import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "avatar",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=users.models.avatar_directory_path,
                    ),
                ),
                ("date_of_create", models.DateTimeField(auto_now_add=True)),
                (
                    "last_connect",
                    models.DateField(blank=True, help_text="Последний вход", null=True),
                ),
                ("phone", models.CharField(blank=True, max_length=18, null=True)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Администратор"),
                            ("OPERATOR", "Оператор"),
                            ("CUSTOMER", "Заказчик"),
                            ("CONTRACTOR", "Исполнитель"),
                            ("OTHER", "Не назначен"),
                        ],
                        default="OTHER",
                        max_length=50,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "db_table": "user",
            },
            managers=[
                ("objects", users.models.MyUserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Contractor",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("users.user",),
            managers=[
                ("objects", users.models.ContractorManager()),
            ],
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("users.user",),
            managers=[
                ("objects", users.models.CustomerManager()),
            ],
        ),
        migrations.CreateModel(
            name="Operator",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("users.user",),
            managers=[
                ("objects", users.models.OperatorManager()),
            ],
        ),
        migrations.CreateModel(
            name="CustomerProfile",
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
                (
                    "linked_operators",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Операторы",
                        null=True,
                        related_name="customers",
                        to="users.operator",
                        verbose_name="Операторы <-> Заказчики",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to="users.customer",
                    ),
                ),
            ],
        ),
    ]
