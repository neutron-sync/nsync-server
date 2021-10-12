from django.db import models
from django.db.models import Count


class SyncKey(models.Model):
  name = models.CharField(max_length=75)

  created = models.DateTimeField(auto_now_add=True, db_index=True)
  modified = models.DateTimeField(auto_now=True)

  owner = models.ForeignKey('account.User', on_delete=models.CASCADE)

  class Meta:
    ordering = ('-created',)
    unique_together = [
      ["name", "owner"],
    ]

  def __str__(self):
    return f"{self.owner}-{self.name}"

  def wipe(self):
    for file in SyncFile.objects.filter(key=self):
      file.wipe()

    FileTransaction.objects.filter(key=self).delete()
    self.delete()


class SyncFile(models.Model):
  path = models.CharField(max_length=1024)

  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)

  key = models.ForeignKey(SyncKey, on_delete=models.CASCADE)

  class Meta:
    ordering = ('-created',)
    unique_together = [
      ["path", "key"],
    ]

  def __str__(self):
    return self.path

  @property
  def latest_version(self):
    return self.fileversion_set.all().first()

  @property
  def latest(self):
    if not hasattr(self, '_latest'):
      self._latest = self.latest_version

    return self._latest

  @property
  def raw_id(self):
    return self.id

  def wipe(self):
    for v in self.fileversion_set.exclude(efile__isnull=True):
      v.efile.delete(save=False)

    self.fileversion_set.all().delete()
    self.delete()

  @classmethod
  def clear_empty(cls, key):
    return cls.objects.annotate(numvers=Count('fileversion')).filter(key=key, numvers=0).delete()


class FileTransaction(models.Model):
  key = models.ForeignKey(SyncKey, on_delete=models.CASCADE)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ('-created',)
    unique_together = [
      ["created", "key"],
    ]

  def __str__(self):
    return '{} {}'.format(self.key, self.id)

  @property
  def raw_id(self):
    return self.id

  @property
  def file_count(self):
    return self.fileversion_set.count()

  def wipe(self):
    for v in self.fileversion_set.all():
      if v.efile:
        v.efile.delete(save=False)

      v.wipe()

    self.delete()


class FileVersion(models.Model):
  efile = models.FileField(upload_to='sync/%Y/%m/%d/', blank=True, null=True)
  uhash = models.CharField(max_length=512, blank=True, null=True, db_index=True)
  permissions = models.PositiveSmallIntegerField(default=0o755)
  is_dir = models.BooleanField(default=False)
  timestamp = models.DateTimeField()

  created = models.DateTimeField(auto_now_add=True)

  sync_file = models.ForeignKey(SyncFile, on_delete=models.CASCADE)
  transaction = models.ForeignKey(FileTransaction, on_delete=models.CASCADE)

  class Meta:
    ordering = ('-created',)
    get_latest_by = 'created'
    index_together = [
      ["sync_file", "created"],
    ]

  def __str__(self):
    return f'{self.sync_file.path} {self.uhash}'

  @property
  def short_uhash(self):
    if self.uhash:
      return self.uhash[:7]

    return ''

  @property
  def download(self):
    if self.efile:
      return self.efile.url

  @property
  def linux_perm(self):
    octal = oct(self.permissions)[-3:]
    result = ""
    value_letters = [(4, "r"), (2, "w"), (1, "x")]

    for digit in [int(n) for n in str(octal)]:
      for value, letter in value_letters:
        if digit >= value:
          result += letter
          digit -= value

        else:
          result += '-'

    return result

  @property
  def raw_id(self):
    return self.id

  def wipe(self):
    if self.efile:
      self.efile.delete(save=False)

    file = self.sync_file
    self.delete()

    if file.fileversion_set.count() == 0:
      file.delete()
