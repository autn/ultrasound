# from crequest.middleware import CrequestMiddleware
from django import forms
from servey.models import UserInfo
from django.contrib.auth.models import User


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields =  "__all__"

