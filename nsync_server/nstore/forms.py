import uuid

from django import forms
from django.core.files.base import ContentFile

from nsync_server.nstore.models import SyncKey, SyncFile, FileVersion


class AddKeyForm(forms.ModelForm):
	class Meta:
		model = SyncKey
		fields = ('name',)


class SaveVersionForm(forms.Form):
	key = forms.CharField()
	path = forms.CharField()
	uhash = forms.CharField(required=False)
	permissions = forms.IntegerField()
	is_dir = forms.BooleanField()
	body = forms.CharField(required=False)

	def save_file(self, key, transaction):
		file = SyncFile.objects.filter(key=key, path=self.cleaned_data['path']).first()
		if file is None:
			file = SyncFile(key=key, path=self.cleaned_data['path'])
			file.save()

		# todo: save version
		version = FileVersion(
			uhash = self.cleaned_data['uhash'],
			permissions = self.cleaned_data['permissions'],
			is_dir = self.cleaned_data['is_dir'],
			sync_file = file,
			transaction = transaction,
		)
		version.save()

		if self.cleaned_data['body']:
			content = ContentFile(self.cleaned_data['body'])
			filename = '{}.etxt'.format(uuid.uuid4())
			version.efile.save(filename, content=content)

		file.modified = timezone.now()
		file.save()
