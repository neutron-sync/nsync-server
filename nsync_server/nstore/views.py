from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404

from nsync_server.nstore.models import FileVersion, SyncFile


@login_required
@permission_required('nstore.delete_fileversion', raise_exception=True)
def wipe_version(request, vid):
  version = get_object_or_404(FileVersion, id=vid)
  file = version.sync_file
  version.wipe()
  messages.success(request, 'Version Wiped')

  file = SyncFile.objects.filter(id=file.id).first()
  if file:
    return http.HttpResponseRedirect(f"/admin/nstore/syncfile/{file.id}/change/")

  return http.HttpResponseRedirect("/admin/nstore/syncfile/")
