from django.contrib import admin

from nsync_server.nstore.models import SyncKey, SyncFile, FileTransaction, FileVersion


@admin.register(SyncKey)
class KeyAdmin(admin.ModelAdmin):
  list_display = ('name', 'owner', 'created')
  date_hierarchy = 'created'
  search_fields = ('name', 'owner__username')

  raw_id_fields = ('owner',)


class VersionInline(admin.TabularInline):
  model = FileVersion
  raw_id_fields = ('transaction', 'sync_file')


@admin.register(SyncFile)
class FileAdmin(admin.ModelAdmin):
  list_display = ('path', 'key', 'created', 'modified')
  date_hierarchy = 'modified'
  search_fields = ('path', 'key__name')

  raw_id_fields = ('key',)

  inlines = (VersionInline,)


@admin.register(FileTransaction)
class TransactionAdmin(admin.ModelAdmin):
  list_display = ('key', 'created')
  date_hierarchy = 'created'
  inlines = (VersionInline,)
  raw_id_fields = ('key',)
