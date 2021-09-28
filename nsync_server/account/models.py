from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):

  def __str__(self):
    return self.username

  @property
  def name(self):
    if self.first_name and self.last_name:
      return '{} {}'.format(self.first_name, self.last_name)

    elif self.first_name:
      return self.first_name

    elif self.last_name:
      return self.last_name

    elif self.email:
      return self.email

    return self.username

  @property
  def has_credit(self):
    if hasattr(self, 'credit_set'):
      now = timezone.now()
      credit = self.credit_set.filter(expiration__gte=now).first()
      if credit:
        return True

      return False

    return True

  @property
  def latest_credit(self):
    if hasattr(self, 'credit_set'):
      now = timezone.now()
      return self.credit_set.filter(expiration__gte=now).first()
