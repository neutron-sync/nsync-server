from django import forms

from nstore.models import SyncKey, SyncFile, FileVersion


class AddKeyForm(forms.ModelForm):
	class Meta:
		model = SyncKey
		fields = ('name',)
