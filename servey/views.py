from django.shortcuts import render, redirect, render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.http import JsonResponse, HttpResponseRedirect
from servey.models import TRAINING_TYPE, TRAINING_LEVEL, ACCURACY_THRESHOLD, CONFIDENCE_LEVEL, EXPERIENCE_NUMBER, UserInfo
from servey.forms import UserInfoForm
# Create your views here.


def index(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)
        user_info = UserInfo.objects.get(user__pk=user.id)
        if user_info.training_type:
            return redirect('take_the_test')
        if request.method == 'POST':
            # user = get_object_or_404(User, pk=request.user.id)
            user_info = UserInfo.objects.filter(user__pk=user.id).update(training_type=request.POST['training_type'])
            return redirect('take_the_test')
        else:
            context = {
                'training_type': TRAINING_TYPE,
            }
        return render(request, 'servey/index.html', context)
    return render(request, 'servey/index.html')


def take_the_test(request):
    return render(request, 'servey/index.html')


# User register, login, logout
def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user = User.objects.create_user(username, email, password)
        user.save()

        data = {
            'institution': request.POST['institution'],
            'training_level': request.POST['training_level'],
            'experience': request.POST['experience_number'],
            'confidence_level': request.POST['confidence_level'],
            'user': user.id
        }
        form = UserInfoForm(data)

        if user is not None and form.is_valid():
            login(request, user)
            # messages.success(request, 'Register Successfully')

            user_info = form.save()
            user_info.institution = form.cleaned_data['institution']
            user_info.training_level = form.cleaned_data['training_level']
            user_info.experience = form.cleaned_data['experience']
            user_info.confidence_level = form.cleaned_data['confidence_level']
            user_info.user = user
            user_info.save()

            return redirect('index')
        else:
            return render_to_response('user/register.html', {'form': form})
    else:
        context = {
                'training_level': TRAINING_LEVEL,
                'confidence_level': CONFIDENCE_LEVEL,
                'experience_number': EXPERIENCE_NUMBER
             }
        return render(request, "user/register.html", context)


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successfully')
            return redirect('index')
        else:
            messages.error(request, 'Username or password not correct')
            return redirect('user_login')
    else:
        return render(request, "user/login.html")


@login_required(login_url='/login')
def user_logout(request):
    logout(request)
    return redirect('index')

