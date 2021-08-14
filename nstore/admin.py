from django.contrib import admin

from nstore.models import SyncKey, SyncFile, FileVersion

@admin.register(SyncKey)
class KeyAdmin(admin.ModelAdmin):
  list_display = ('name', 'owner', 'created')
  date_hierarchy = 'created'
  search_fields = ('name', 'owner__username')

  raw_id_fields = ('owner',)


class VersionInline(admin.TabularInline):
   model = FileVersion


@admin.register(SyncFile)
class FileAdmin(admin.ModelAdmin):
	list_display = ('path', 'key', 'created', 'modified')
	list_filter = ('modified',)
	search_fields = ('path', 'key__name')

	raw_id_fields = ('key',)

	inlines = (VersionInline,)
