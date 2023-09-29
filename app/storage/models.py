from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class Component(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Order(models.Model):
    components = models.ManyToManyField(Component, through='OrderComponent')
    date_shipment = models.DateField(
        verbose_name="Дата отгрузки", blank=True, null=True
    )
