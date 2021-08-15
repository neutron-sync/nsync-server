from django import forms

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

	def save_file(self, key, trans):
		file = SyncFile.objects.filter(key=key, path=self.cleaned_data['path']).first()
		if file is None:
			file = SyncFile(key=key, path=self.cleaned_data['path'])
			file.save()

		# todo: save version
		version = FileVersion()
		version.save()

		file.modified = timezone.now()
		file.save()
