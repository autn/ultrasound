from django.shortcuts import render
from django.shortcuts import render, redirect, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.defaultfilters import slugify
# Create your views here.


# get list blog
def index(request):
    return render(request, 'servey/index.html')


# User register, login, logout
def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        user = User.objects.create_user(username, email, password)
        user.save()
        if user is not None:
            login(request, user)
            messages.success(request, 'Register Successfully')
            return redirect('blog_index')
        else:
            raise forms.ValidationError(
                'Register credentials not valid'
            )
    else:
        return render(request, "user/register.html")


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successfully')
            return redirect('blog_index')
        else:
            messages.success(request, 'Login credentials not valid')
            return redirect('user_login')
    else:
        return render(request, "user/login.html")


@login_required(login_url='/login')
def user_logout(request):
    logout(request)
    return redirect('user_login')
