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
