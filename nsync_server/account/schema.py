from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.urls import reverse

import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType, ErrorType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoFormMutation

from django_2fa.decorators import is_mfa_user
from django_2fa.models import MFARequest

from nsync_server.account.models import User
from nsync_server.account.forms import LoginForm


class UserType(DjangoObjectType):
  sessionExpiration = graphene.Int()
  has_credit = graphene.Boolean()

  class Meta:
    model = User
    interfaces = (relay.Node,)
    filter_fields = []
    fields = ('first_name', 'last_name', 'username', 'email')

  @classmethod
  def get_queryset(cls, queryset, info):
    if info.context.user.is_authenticated:
      return queryset.filter(id=info.context.user.id)

    return User.objects.none()

  def resolve_sessionExpiration(self, info):
    if hasattr(info.context, 'session') and info.context.session:
      return int(info.context.session.get_expiry_date().timestamp())

    return 0


class LoginMutation(DjangoFormMutation):
  user = graphene.Field(UserType)
  mfa_url = graphene.String()

  class Meta:
    form_class = LoginForm

  @classmethod
  def mutate_and_get_payload(cls, root, info, **input):
    form = cls.get_form(root, info, **input)
    if form.is_valid():
      mfa_url = None

      user = authenticate(
        info.context,
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password'],
      )
      login(info.context, user)

      if is_mfa_user(user):
        request = MFARequest.generate(user)
        mfa_url = reverse('django_2fa:mfa-request', args=[request.token])
        mfa_url = "{}://{}{}".format(info.context.scheme, info.context.get_host(), mfa_url)

      return cls(user=user, mfa_url=mfa_url)

    else:
      errors = ErrorType.from_errors(form.errors)
      return cls(errors=errors)


class Query:
  users = DjangoFilterConnectionField(UserType)


class Mutation:
  login = LoginMutation.Field()
