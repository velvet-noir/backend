from django.db import models
from django.contrib.auth.models import User
from django_minio_backend import MinioBackend


class Server(models.Model):
    name = models.CharField(max_length=100)
    image = models.FileField(
        verbose_name="Object Upload", storage=MinioBackend(bucket_name="mybucket")
    )
    mini_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class ServerSpecification(models.Model):
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="specifications"
    )
    description = models.TextField()
    processor = models.CharField(max_length=100)
    ram = models.CharField(max_length=100)
    disk = models.CharField(max_length=100)
    internet_speed = models.CharField(max_length=100)

    def __str__(self):
        return self.server.name

    class Meta:
        ordering = ["id"]
        verbose_name = "Характеристика услуги"
        verbose_name_plural = "Характеристики услуг"


class ApplicationStatus(models.TextChoices):
    DRAFT = "DRAFT"
    DELETED = "DELETED"
    FORMED = "FORMED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class Application(models.Model):
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_creator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="created_applications",
    )
    user_moderator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="moderated_applications",
    )

    def __str__(self):
        return f"Заявка № {self.id}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["created_at"]


class ApplicationServer(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="servers"
    )
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="applications"
    )

    class Meta:
        unique_together = ("application", "server")
        verbose_name = "Услуга в заявке"
        verbose_name_plural = "Услуги в заявках"

    def __str__(self):
        return f"Заявка {self.application.id} - Услуга {self.server.name}"
