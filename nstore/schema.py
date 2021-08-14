import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation

from nstore.models import SyncKey, SyncFile, FileVersion
from nstore.forms import AddKeyForm


class SyncKeyNode(DjangoObjectType):
	class Meta:
		model = SyncKey
		filter_fields = ['name', 'id']
		fields = ('name', 'created', 'modified', 'id', 'syncfile_set')
		interfaces = (relay.Node, )

	@classmethod
	def get_queryset(cls, queryset, info):
		if info.context.user.is_authenticated:
			return queryset.filter(owner=info.context.user)

		return queryset.none()


class SyncFileNode(DjangoObjectType):
	class Meta:
		model = SyncFile
		filter_fields = ['path', 'id', 'key']
		fields = ('path', 'created', 'modified', 'id', 'key', 'fileversion_set')
		interfaces = (relay.Node, )

	@classmethod
	def get_queryset(cls, queryset, info):
		if info.context.user.is_authenticated:
			return queryset.filter(key__owner=info.context.user)

		return queryset.none()


class FileVersionNode(DjangoObjectType):
	download = graphene.String()

	class Meta:
		model = FileVersion
		filter_fields = ['id', 'sync_file']
		fields = ('created', 'sync_file', 'id')
		interfaces = (relay.Node, )

	@classmethod
	def get_queryset(cls, queryset, info):
		if info.context.user.is_authenticated:
			return queryset.filter(sync_file__key__owner=info.context.user)

		return queryset.none()


class AddKeyMutation(DjangoModelFormMutation):
	class Meta:
		form_class = AddKeyForm
		exclude_fields = ['id']


class Query:
  sync_keys = DjangoFilterConnectionField(SyncKeyNode)
  sync_files = DjangoFilterConnectionField(SyncFileNode)
  file_versions = DjangoFilterConnectionField(FileVersionNode)


class Mutation:
	add_key = AddKeyMutation.Field()
