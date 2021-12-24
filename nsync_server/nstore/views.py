from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django_2fa.decorators import mfa_login_required, mfa_user_if_authed
from graphene_django.views import GraphQLView

from nsync_server.nstore.models import FileVersion, SyncFile

GRAPHQL_VIEW = GraphQLView.as_view(graphiql=True)


@csrf_exempt
@mfa_user_if_authed
def graphql(request):
  return GRAPHQL_VIEW(request)


@mfa_login_required
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
