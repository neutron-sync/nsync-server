from django import forms

from nsync_server.account.models import User


class LoginForm(forms.Form):
  username = forms.CharField(required=True)
  password = forms.CharField(required=True)

  def clean(self):
    cleaned_data = super().clean()
    username = cleaned_data.get("username")
    password = cleaned_data.get("password")

    user = User.objects.filter(username=username).first()
    if user:
      if user.check_password(password):
        return cleaned_data

      raise forms.ValidationError('Invalid Password', code='invalid')

    raise forms.ValidationError('Invalid Username', code='invalid')
