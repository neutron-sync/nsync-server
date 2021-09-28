from django.contrib import admin
from django.contrib import messages
from django.utils.safestring import mark_safe

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
  readonly_fields = ('_wipe',)
  can_delete = False

  def _wipe(self, obj):
    if obj and obj.id:
      return mark_safe(
        f'<a href="/admin/nstore/fileversion/{obj.id}/wipe/" onclick="return confirm(\'Are you sure you wish to wipe?\')">Wipe {obj.id}</a>'
      )

    return '---'


@admin.action(description='Clear all versions and delete file')
def wipe(modeladmin, request, queryset):
  count = queryset.count()

  for file in queryset:
    file.wipe()

  messages.success(request, f'{count} Files Wiped')


@admin.register(SyncFile)
class FileAdmin(admin.ModelAdmin):
  list_display = ('path', 'key', 'created', 'modified')
  date_hierarchy = 'modified'
  search_fields = ('path', 'key__name', 'owner__username')
  actions = [wipe]

  raw_id_fields = ('key',)

  inlines = (VersionInline,)


@admin.action(description='Clear all versions and delete files')
def wipe_transaction(modeladmin, request, queryset):
  count = queryset.count()

  for trans in queryset:
    trans.wipe()

  messages.success(request, f'{count} Transactions Wiped')


@admin.register(FileTransaction)
class TransactionAdmin(admin.ModelAdmin):
  list_display = ('key', 'id', 'file_count', 'created')
  date_hierarchy = 'created'
  inlines = (VersionInline,)
  raw_id_fields = ('key',)
  actions = [wipe_transaction]
