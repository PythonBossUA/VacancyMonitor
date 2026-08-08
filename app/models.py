from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class Vacancy(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    publication_date = models.DateField(null=False, blank=False)
    url = models.URLField(null=False, blank=False)
