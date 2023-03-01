from django.db import models


class DictionaryTypeManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class DictionaryType(models.Model):
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=50, verbose_name="Код типа словаря", unique=True)
    description = models.CharField(max_length=150, verbose_name="Описание типа словаря")
    objects = DictionaryTypeManager()

    def __str__(self):
        return self.code


class Dictionary(models.Model):
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    type_dict = models.ForeignKey(
        DictionaryType, verbose_name="Тип словаря", on_delete=models.CASCADE, null=True
    )

    code = models.CharField(max_length=50, verbose_name="Код словаря", unique=True)
    description = models.CharField(max_length=150, verbose_name="Описание словаря")

    def __str__(self):
        return self.description

    @classmethod
    def status_tickets(cls):
        dt = DictionaryType.objects.get(code="status_ticket")
        return cls.objects.filter(type_dict=dt)

    @classmethod
    def get_status_ticket(cls, code):
        dt = DictionaryType.objects.get(code="status_ticket")
        return cls.objects.get(type_dict=dt, code=code)

    @classmethod
    def get_type_ticket(cls, code):
        dt = DictionaryType.objects.get(code="type_ticket")
        return cls.objects.get(type_dict=dt, code=code)

    def get_status_color(self):
        if self.type_dict != DictionaryType.objects.get(code="status_ticket"):
            return
        color = {
            "work": "blue",
            "search_contractor": "orange",
            "consideration": "teal",
            "revision": "yellow",
            "done": "green",
            "new": "violet",
            "testing": "pink",
        }
        return color.get(self.code, "detail")
