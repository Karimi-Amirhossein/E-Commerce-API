from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """ Custom user model based on Django's AbstractUser. """

    def __str__(self):
        """Return a human-readable string representation of the user."""
        return self.username
