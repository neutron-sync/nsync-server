from django.db import models


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
    return self.name


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


class FileTransaction(models.Model):
  key = models.ForeignKey(SyncKey, on_delete=models.CASCADE)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ('-created',)
    unique_together = [
      ["created", "key"],
    ]

  def __str__(self):
    return '{} {}'.format(self.key.name, self.created.isoformat())


class FileVersion(models.Model):
  efile = models.FileField(upload_to='sync/%Y/%m/%d/', blank=True, null=True)
  uhash = models.CharField(max_length=512, blank=True, null=True)
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
  def download(self):
    if self.efile:
      return self.efile.url

  @property
  def linux_perm(self):
    octal = oct(self.permissions)[-3:]
    result = ""
    value_letters = [(4,"r"),(2,"w"),(1,"x")]

    for digit in [int(n) for n in str(octal)]:
      for value, letter in value_letters:
        if digit >= value:
          result += letter
          digit -= value

        else:
          result += '-'

    return result
