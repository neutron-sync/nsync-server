import uuid

from django import forms
from django.core.files.base import ContentFile
from django.utils import timezone

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
	fileType = forms.CharField()
	ebody = forms.CharField(required=False, max_length=1024 * 1024 * 5, min_length=1)

	def save_file(self, key, transaction):
		file = SyncFile.objects.filter(key=key, path=self.cleaned_data['path']).first()
		if file is None:
			file = SyncFile(key=key, path=self.cleaned_data['path'])
			file.save()

		uhash = self.cleaned_data['uhash']
		if not uhash:
			uhash = None

		version = FileVersion(
			uhash = uhash,
			permissions = self.cleaned_data['permissions'],
			is_dir = self.cleaned_data['fileType'] == 'dir',
			sync_file = file,
			transaction = transaction,
		)
		version.save()

		if self.cleaned_data['ebody']:
			print(type(self.cleaned_data['ebody']), self.cleaned_data['ebody'])
			content = ContentFile(self.cleaned_data['ebody'])
			filename = '{}.etxt'.format(uuid.uuid4())
			version.efile.save(filename, content=content)

		file.modified = timezone.now()
		file.save()
		return version
