from django.contrib.auth.models import AbstractUser
from django.db import models


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
