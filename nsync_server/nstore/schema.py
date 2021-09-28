import json

from django.core.cache import cache
from django.utils import timezone

import django_filters
import graphene
from graphene import relay
from graphene.types.scalars import Scalar
from graphene_django.types import DjangoObjectType, ErrorType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation, DjangoFormMutation

from haikunator import Haikunator

from nsync_server.nsync.graphene import AuthMutation
from nsync_server.nstore.models import SyncKey, SyncFile, FileVersion, FileTransaction
from nsync_server.nstore.forms import AddKeyForm, SaveVersionForm, StartKeyExchangeForm, CompleteKeyExchangeForm


class BigInt(Scalar):

  @staticmethod
  def coerce_int(value):
    try:
      num = int(value)
    except ValueError:
      try:
        num = int(float(value))
      except ValueError:
        return None
    return num

  serialize = coerce_int
  parse_value = coerce_int

  @staticmethod
  def parse_literal(ast):
    if isinstance(ast, IntValueNode):
      return int(ast.value)


class SyncKeyNode(DjangoObjectType):

  class Meta:
    model = SyncKey
    filter_fields = ['name', 'id']
    fields = ('name', 'created', 'modified', 'id', 'syncfile_set')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated and info.context.user.has_credit:
      return queryset.filter(owner=info.context.user)

    return queryset.none()


class FileTransactionFilter(django_filters.FilterSet):
  key = django_filters.CharFilter(field_name='key__name')

  class Meta:
    model = FileTransaction
    fields = ['id', 'key']


class FileTransactionNode(DjangoObjectType):
  raw_id = BigInt()

  class Meta:
    model = FileTransaction
    filter_fields = ['id', 'key']
    fields = ('id', 'key', 'fileversion_set')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated and info.context.user.has_credit:
      return queryset.filter(key__owner=info.context.user)

    return queryset.none()


class SyncFileFilter(django_filters.FilterSet):
  key = django_filters.CharFilter(field_name='key__name')

  class Meta:
    model = SyncFile
    fields = ['id', 'key', 'path']


class FileVersionNode(DjangoObjectType):
  download = graphene.String()
  raw_id = BigInt()

  class Meta:
    model = FileVersion
    filter_fields = ['id', 'sync_file']
    fields = ('created', 'id', 'transaction', 'uhash', 'permissions', 'timestamp', 'is_dir')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated and info.context.user.has_credit:
      return queryset.filter(sync_file__key__owner=info.context.user)

    return queryset.none()


class SyncFileNode(DjangoObjectType):
  latest_version = graphene.Field(FileVersionNode)
  raw_id = BigInt()

  class Meta:
    model = SyncFile
    filter_fields = ['path', 'id', 'key']
    fields = ('path', 'created', 'modified', 'id', 'key', 'fileversion_set')
    interfaces = (relay.Node,)

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated and info.context.user.has_credit:
      return queryset.filter(key__owner=info.context.user)

    return queryset.none()


class AddKeyMutation(AuthMutation, DjangoModelFormMutation):

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


class SaveVersionMutation(AuthMutation, DjangoFormMutation):
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


class StartKeyExchangeMutation(AuthMutation, DjangoFormMutation):
  phrase = graphene.String()

  class Meta:
    form_class = StartKeyExchangeForm

  @classmethod
  def perform_mutate(cls, form, info):
    haikunator = Haikunator()

    data = json.dumps({
      'key': form.cleaned_data['key'],
      'salt': form.cleaned_data['salt'],
      'etext': form.cleaned_data['etext'],
      'user': info.context.user.id,
    })
    while 1:
      phrase = haikunator.haikunate()
      value = cache.get(f'exchange-{phrase}')
      if value is None:
        break

    cache.set(f'exchange-{phrase}', data, 15 * 60)
    return cls(errors=[], phrase=phrase, **form.cleaned_data)


class CompleteKeyExchangeMutation(AuthMutation, DjangoFormMutation):
  key = graphene.String()
  salt = graphene.String()
  etext = graphene.String()

  class Meta:
    form_class = CompleteKeyExchangeForm

  @classmethod
  def perform_mutate(cls, form, info):
    ckey = 'exchange-{}'.format(form.cleaned_data['phrase'])
    value = cache.get(ckey)
    key = ''
    salt = ''
    etext = ''

    if value:
      data = json.loads(value)
      user = data['user']

      if user == info.context.user.id:
        key = data['key']
        salt = data['salt']
        etext = data['etext']
        cache.delete(ckey)

    return cls(errors=[], key=key, salt=salt, etext=etext, **form.cleaned_data)


class Query:
  sync_keys = DjangoFilterConnectionField(SyncKeyNode)
  sync_files = DjangoFilterConnectionField(SyncFileNode, filterset_class=SyncFileFilter)
  file_versions = DjangoFilterConnectionField(FileVersionNode)
  file_transactions = DjangoFilterConnectionField(FileTransactionNode, filterset_class=FileTransactionFilter)


class Mutation:
  add_key = AddKeyMutation.Field()
  save_version = SaveVersionMutation.Field()
  start_key_exchange = StartKeyExchangeMutation.Field()
  complete_key_exchange = CompleteKeyExchangeMutation.Field()
