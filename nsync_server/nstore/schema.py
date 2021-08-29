from django.utils import timezone

import django_filters
import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType, ErrorType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation, DjangoFormMutation

from nsync_server.nstore.models import SyncKey, SyncFile, FileVersion, FileTransaction
from nsync_server.nstore.forms import AddKeyForm, SaveVersionForm, StartKeyExchangeForm


class SyncKeyNode(DjangoObjectType):

  class Meta:
    model = SyncKey
    filter_fields = ['name', 'id']
    fields = ('name', 'created', 'modified', 'id', 'syncfile_set')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated:
      return queryset.filter(owner=info.context.user)

    return queryset.none()


class FileTransactionFilter(django_filters.FilterSet):
  key = django_filters.CharFilter(field_name='key__name')

  class Meta:
    model = FileTransaction
    fields = ['id', 'key']


class FileTransactionNode(DjangoObjectType):

  class Meta:
    model = FileTransaction
    filter_fields = ['id', 'key']
    fields = ('id', 'key', 'fileversion_set')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated:
      return queryset.filter(key__owner=info.context.user)

    return queryset.none()


class SyncFileFilter(django_filters.FilterSet):
  key = django_filters.CharFilter(field_name='key__name')

  class Meta:
    model = SyncFile
    fields = ['id', 'key', 'path']


class FileVersionNode(DjangoObjectType):
  download = graphene.String()

  class Meta:
    model = FileVersion
    filter_fields = ['id', 'sync_file']
    fields = ('created', 'id', 'transaction', 'uhash', 'permissions', 'timestamp', 'is_dir')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated:
      return queryset.filter(sync_file__key__owner=info.context.user)

    return queryset.none()


class SyncFileNode(DjangoObjectType):
  latest_version = graphene.Field(FileVersionNode)

  class Meta:
    model = SyncFile
    filter_fields = ['path', 'id', 'key']
    fields = ('path', 'created', 'modified', 'id', 'key', 'fileversion_set')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated:
      return queryset.filter(key__owner=info.context.user)

    return queryset.none()


class AddKeyMutation(DjangoModelFormMutation):

  class Meta:
    form_class = AddKeyForm
    exclude_fields = ['id']

  @classmethod
  def perform_mutate(cls, form, info):
    obj = form.save(commit=False)
    obj.owner = info.context.user
    obj.save()
    kwargs = {cls._meta.return_field_name: obj}
    return cls(errors=[], **kwargs)


class SaveVersionMutation(DjangoFormMutation):
  transaction = graphene.Int()

  class Meta:
    form_class = SaveVersionForm

  @classmethod
  def perform_mutate(cls, form, info):
    key = SyncKey.objects.filter(name=form.cleaned_data['key'], owner=info.context.user).first()
    if key is None:
      return cls(errors=[ErrorType(field='key', messages='Invalid key')])

    if not hasattr(info.context, 'transaction'):
      trans = FileTransaction(key=key)
      trans.save()
      info.context.transaction = trans

    version = form.save_file(key, info.context.transaction)
    return cls(errors=[], transaction=version.transaction.id, **form.cleaned_data)


class StartKeyExchangeForm(DjangoFormMutation):
  phrase = graphene.String()

  class Meta:
    form_class = StartKeyExchangeForm

  @classmethod
  def perform_mutate(cls, form, info):
    return cls(errors=[], phrase=phrase, **form.cleaned_data)


class Query:
  sync_keys = DjangoFilterConnectionField(SyncKeyNode)
  sync_files = DjangoFilterConnectionField(SyncFileNode, filterset_class=SyncFileFilter)
  file_versions = DjangoFilterConnectionField(FileVersionNode)
  file_transactions = DjangoFilterConnectionField(FileTransactionNode, filterset_class=FileTransactionFilter)


class Mutation:
  add_key = AddKeyMutation.Field()
  save_version = SaveVersionMutation.Field()
