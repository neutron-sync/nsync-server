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


class FileVersion(models.Model):
	efile = models.FileField(upload_to='sync/%Y/%m/%d/')
	uhash = models.CharField(max_length=512)
	permissions = models.PositiveSmallIntegerField(default=0o755)

	created = models.DateTimeField(auto_now_add=True)

	sync_file = models.ForeignKey(SyncFile, on_delete=models.CASCADE)

	class Meta:
		ordering = ('-created',)
		get_latest_by = 'created'
		index_together = [
    	["sync_file", "created"],
		]

	def __str__(self):
		return f'{self.sync_file.path} {self.uhash}'

	def download(self):
		return self.efile.url
