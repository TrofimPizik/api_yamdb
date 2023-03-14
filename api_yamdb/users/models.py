from django.db import models
from django.contrib.auth.models import AbstractUser

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, USER),
    (MODERATOR, MODERATOR),
    (ADMIN, ADMIN),
)

class User(AbstractUser):
    role = models.CharField(
        choices=ROLES,
        default=USER,
        verbose_name='Уровень пользователя',
        max_length=255
    )
    email = models.EmailField(
        verbose_name='E-Mail',
        unique=True,
    )
    bio = models.TextField(
        verbose_name="О себе",
        blank=True,
        null=True,
    ) 
