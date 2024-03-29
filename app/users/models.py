import uuid
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.conf import settings
from django.urls import reverse


def avatar_directory_path(instance, filename):
    return f"user_{instance.id}/{filename}"


class UserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})


class OperatorManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.OPERATOR)


class CustomerManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.CUSTOMER)


class ContractorManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.CONTRACTOR)


class ManufacturerManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.MANUFACTURER)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Администратор"
        OPERATOR = "OPERATOR", "Оператор"
        CUSTOMER = "CUSTOMER", "Заказчик"
        CONTRACTOR = "CONTRACTOR", "Исполнитель"
        MANUFACTURER = "MANUFACTURER", "Производство"
        OTHER = "OTHER", "Не назначен"

    avatar = models.FileField(
        upload_to=avatar_directory_path, null=True, blank=True, verbose_name="Аватар"
    )
    date_of_create = models.DateTimeField(auto_now_add=True)
    last_connect = models.DateField(help_text="Последний вход", null=True, blank=True)
    phone = models.CharField("Телефон", max_length=72, blank=True, null=True)
    role = models.CharField(max_length=50, choices=Role.choices, verbose_name="Роль")
    telegram_id = models.CharField("Telegram ID", max_length=100, blank=True, null=True)
    email_notify = models.BooleanField("Уведомлять по email", default=True)
    telegram_notify = models.BooleanField("Уведомлять в Telegram", default=False)

    base_role = Role.OTHER
    token = models.UUIDField(
        editable=False, default=uuid.uuid4, unique=True, db_index=True
    )
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.role:
            self.role = self.base_role
        return super().save(*args, **kwargs)

    def get_customers(self):
        if self.is_staff:
            return Customer.objects.all()
        return Customer.objects.none()

    @property
    def is_has_operator_access(self):
        return self.is_operator or self.groups.filter(name=self.Role.OPERATOR).exists()

    @property
    def is_operator(self):
        return self.role == self.Role.OPERATOR

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_contractor(self):
        return self.role == self.Role.CONTRACTOR

    @property
    def is_manufacturer(self):
        return self.role == self.Role.MANUFACTURER

    def get_role_user(self) -> "Operator | Customer | Contractor":
        type_user = {
            "OPERATOR": Operator,
            "CUSTOMER": Customer,
            "CONTRACTOR": Contractor,
        }
        return type_user.get(self.role, User).objects.get(pk=self.pk)

    class Meta:
        db_table = "user"

    def get_avatar(self):
        if not self.avatar.name:
            return f"{settings.MEDIA_URL}avatar.jpg"
        return f"{settings.MEDIA_URL}{self.avatar.name}"

    def get_ticket_filter(self):
        return {"creator": self.pk}

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_absolute_url(self):
        return reverse("account")


class Customer(User):
    class Meta:
        proxy = True
        verbose_name = "Заказчик"
        verbose_name_plural = "Заказчики"

    base_role = User.Role.CUSTOMER
    objects = CustomerManager()

    def get_ticket_filter(self):
        return {"customer_id": self.pk}

    def get_customers(self) -> models.QuerySet:
        return Customer.objects.filter(pk=self.pk)

    def get_parser(self):
        return self.profile.parser

    def get_operators(self) -> models.QuerySet:
        return self.profile.linked_operators.all()

    def short_str(self):
        if self.profile and self.profile.company:
            return self.profile.company
        return super().__str__()

    def __str__(self) -> str:
        if self.profile and self.profile.company:
            if self.first_name and self.last_name:
                return f"{self.profile.company} ({self.first_name} {self.last_name})"
            return self.profile.company
        return super().__str__()


class Operator(User):
    class Meta:
        proxy = True
        verbose_name = "Оператор"
        verbose_name_plural = "Операторы"

    base_role = User.Role.OPERATOR
    objects = OperatorManager()

    def get_customers_id(self):
        return self.customers.values_list("user_id", flat=True)

    def get_customers(self) -> models.QuerySet[Customer]:
        return Customer.objects.filter(pk__in=self.get_customers_id())

    def get_ticket_filter(self) -> dict:
        customers_id = self.get_customers_id()
        return {"customer__in": customers_id}


class Contractor(User):
    class Meta:
        proxy = True
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"

    base_role = User.Role.CONTRACTOR
    objects = ContractorManager()

    def get_ticket_filter(self):
        return {"contractor_id": self.pk}

    def get_customers(self) -> models.QuerySet[Customer]:
        "return empty queryset"
        return Customer.objects.none()


class CustomerProfile(models.Model):
    """
    create in signals
    """

    class Meta:
        verbose_name = "Профиль заказчика"
        verbose_name_plural = "Профили заказчиков"

    user = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="profile"
    )
    linked_operators = models.ManyToManyField(
        Operator,
        verbose_name="Операторы заказчика",
        related_name="customers",
        help_text="Какие операторы могут работать с этим заказчиком",
        null=True,
        blank=True,
    )
    parser = models.CharField(verbose_name="Парсер", max_length=50, default="base")
    company = models.CharField(
        verbose_name="Компания", max_length=100, null=True, blank=True
    )
    _emails = models.CharField(
        verbose_name="Адреса, которые должны быть в копии",
        max_length=500,
        null=True,
        blank=True,
        db_column="emails",
    )

    def __str__(self) -> str:
        return str(self.user)

    @property
    def emails(self) -> list:
        if not self._emails:
            return []
        return [i.strip() for i in self._emails.split(",")]

    @emails.setter
    def emails(self, value: list):
        self._emails = ",".join(value)


class ContractorProfile(models.Model):
    """
    create in signals
    """

    user = models.OneToOneField(
        Contractor, on_delete=models.CASCADE, related_name="profile_contractor"
    )
    city = models.CharField(verbose_name="Город", max_length=50, null=True, blank=True)
    region = models.CharField(
        verbose_name="Область", max_length=100, null=True, blank=True
    )
    company = models.CharField(
        verbose_name="Компания", max_length=100, null=True, blank=True
    )
    note = models.TextField(verbose_name="Примечание", null=True, blank=True)

    def __str__(self) -> str:
        return str(self.user)


class Manufacturer(User):
    class Meta:
        proxy = True
        verbose_name = "Производство"
        verbose_name_plural = "Производства"

    base_role = User.Role.MANUFACTURER
    objects = ManufacturerManager()
