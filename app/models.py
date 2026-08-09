from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)


class Vacancy(models.Model):
    STATUS_CHOICES = [
        ("applied", "Відгукнувся"),
        ("not_interested", "Не цікаво"),
    ]

    name = models.CharField(max_length=255, null=False, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    publication_date = models.DateField(null=False, blank=False)
    url = models.URLField(null=False, blank=False, unique=True)
    category = models.CharField(max_length=21, null=False, blank=False)
    status = models.CharField(
        max_length=31, null=True, blank=True, choices=STATUS_CHOICES, default=None
    )
    is_active = models.BooleanField(default=True)

    @property
    def status_display(self):
        mapping = dict(self.STATUS_CHOICES)
        return mapping.get(self.status, "Без статусу")
