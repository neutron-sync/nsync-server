import uuid

from django import forms
from django.core.files.base import ContentFile
from django.utils import timezone

from nsync_server.nstore.models import SyncKey, SyncFile, FileVersion, FileTransaction


class AddKeyForm(forms.ModelForm):

  class Meta:
    model = SyncKey
    fields = ('name',)


class SaveVersionForm(forms.Form):
  key = forms.CharField()
  path = forms.CharField()
  uhash = forms.CharField(required=False)
  permissions = forms.IntegerField()
  timestamp = forms.DateTimeField()
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
      uhash=uhash,
      permissions=self.cleaned_data['permissions'],
      timestamp=self.cleaned_data['timestamp'],
      is_dir=self.cleaned_data['fileType'] == 'dir',
      sync_file=file,
      transaction=transaction,
    )
    version.save()

    if self.cleaned_data['ebody']:
      content = ContentFile(self.cleaned_data['ebody'].encode())
      filename = '{}.etxt'.format(uuid.uuid4())
      version.efile.save(filename, content=content)

    file.modified = timezone.now()
    file.save()
    return version


class StartKeyExchangeForm(forms.Form):
  key = forms.CharField()
  salt = forms.CharField()
  etext = forms.CharField()


class CompleteKeyExchangeForm(forms.Form):
  phrase = forms.CharField()


class DeleteItemForm(forms.Form):
  DELETE_TYPES = (
    ('file', 'file'),
    ('key', 'key'),
    ('transaction', 'transaction'),
    ('version', 'version'),
  )
  item_type = forms.ChoiceField(choices=DELETE_TYPES)
  item_id = forms.CharField()

  def do_delete(self, user):
    qs = None
    if self.cleaned_data['item_type'] == 'file':
      qs = SyncFile.objects.filter(key__owner=user, id=self.cleaned_data['item_id'])

    elif self.cleaned_data['item_type'] == 'transaction':
      qs = FileTransaction.objects.filter(key__owner=user, id=self.cleaned_data['item_id'])

    elif self.cleaned_data['item_type'] == 'version':
      qs = FileVersion.objects.filter(sync_file__key__owner=user, id=self.cleaned_data['item_id'])

    elif self.cleaned_data['item_type'] == 'key':
      qs = SyncKey.objects.filter(owner=user, name=self.cleaned_data['item_id'])

    if qs and qs.count():
      for obj in qs:
        obj.wipe()

      return True

    return False
