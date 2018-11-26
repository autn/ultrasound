from django.shortcuts import render, redirect, render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from servey.models import TRAINING_TYPE, TRAINING_LEVEL, ACCURACY_THRESHOLD, CONFIDENCE_LEVEL, EXPERIENCE_NUMBER, UserInfo, Video, Result, ResultDetail
from servey.forms import UserInfoForm
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from decimal import Decimal
from django.conf import settings
from django.db.models import Q
# Create your views here.


def index(request):
    context = {
        'training_type': TRAINING_TYPE,
        'percent': ACCURACY_THRESHOLD
    }

    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)
        if request.method == 'POST':
            # UserInfo.objects.filter(user__pk=user.id).update(
            #     training_type=request.POST['training_type'],
            #     accuracy=request.POST['percent']
            # )
            user_exits = UserInfo.objects.filter(user=user).exists()
            if not user_exits:
                UserInfo.objects.create(user=user,training_type=request.POST['training_type'],accuracy=request.POST['percent'])
            else:
                UserInfo.objects.filter(user=user).update(
                    training_type=request.POST['training_type'],
                    accuracy=request.POST['percent']
                )
            return redirect('take_the_test')

        user_info = UserInfo.objects.filter(user=user, training_type__isnull=False).first()
        if user_info is None:
            return render(request, 'servey/index.html', context)
        else:
            return redirect('take_the_test')

    else:
        return render(request, 'servey/index.html', context)


def take_the_test(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)
        random_video = Video.objects.order_by('?').first()
        count_video = Video.objects.count()

        exits_video = ResultDetail.objects.filter(result__user=user)
        answers = Video.ANSWER_CHOICE
        context = {
            'random_video': random_video,
            'answers': answers
        }
        user_info = UserInfo.objects.filter(user=user, training_type__isnull=False).first()
        url = reverse('index')
        if user_info is None:
            return redirect('index')
        return render(request, 'servey/do_test.html', context)
    else:
        return redirect('index')


@csrf_exempt
def answer_response(request):
    question_id = request.POST['question_id']
    answer = request.POST['answer']
    check = Video.objects.filter(pk=question_id, answer=answer).first()
    check_answer_true = Video.objects.filter(pk=question_id).first()
    answer_true = check_answer_true.get_answer_display()

    exits_user = Result.objects.filter(user=request.user, close=False).order_by('-updated_at').first()
    if not exits_user:
        result = Result.objects.create(user_id=request.user.id, close=False)
        ResultDetail.objects.create(answer=answer, result=result, video_id=question_id)
    ResultDetail.objects.create(answer=answer, result=exits_user, video_id=question_id)

    if check is not None:
        data = {
            "status": True,
            "message": "Correct! Ejection fraction is " + answer_true
        }
        return JsonResponse(data, safe=False)

    else:
        data = {
            "status": False,
            "message": "Incorrect. Ejection fraction is " + answer_true
        }
        return JsonResponse(data, safe=False)


@login_required(login_url=settings.LOGIN_URL)
def close_test(request):
    exits_user = Result.objects.filter(user=request.user).order_by('-updated_at').first()
    data = {"status": False, "messages": "Test has already been closed"}

    if request.POST and exits_user is not None:
        result_user = Result.objects.filter(user=request.user, close=False).get()

        if result_user is not None:
            Result.objects.filter(user=request.user).update(close=True)
            return redirect('result_test')
        else:
            return JsonResponse(data, safe=False)
    else:
        return JsonResponse(data, safe=False)


@login_required(login_url=settings.LOGIN_URL)
def result_test(request):
    result = Result.objects.filter(user=request.user, close=True).order_by('-updated_at').first()
    if result is not None:
        # context = {}
        # count_question = ResultDetail.objects.filter(result__user=request.user).count()
        # total_answer = ResultDetail.objects.filter(result__user=request.user)
        #
        # context['true'] = 0
        # context['false'] = 0
        # for query_answer in total_answer:
        #     video = query_answer.video.answer
        #     answer_result = query_answer.answer
        #     if video == answer_result:
        #         context['true'] += 1
        #     else:
        #         context['false'] += 1
        #
        # accuracy = Decimal(context['true'] * 100 / count_question)
        # context = {
        #     "total_views": count_question,
        #     "accuracy": accuracy
        # }
        context = cacu_accuracy(request)
        return render(request, 'servey/result_test.html', context)
    else:
        return JsonResponse({"status": False, "messages": "Test has not been closed"}, safe=False)


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
        email = request.POST['email']
        password = request.POST['password']
        check_exits = User.objects.filter(email=email.lower())
        if not check_exits:
            messages.error(request, 'Email not exits')
            return redirect('user_login')
        check_username = User.objects.get(email=email.lower()).username
        user = authenticate(request, username=check_username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successfully')
            return redirect('index')
        else:
            messages.error(request, 'Username or password not correct')
            return redirect('user_login')
    else:
        return render(request, "user/login.html")


@login_required(login_url=settings.LOGIN_URL)
def user_logout(request):
    logout(request)
    return redirect('index')


@login_required(login_url=settings.LOGIN_URL)
def user_profile(request):
    if request.user.is_authenticated:
        result_detail = Result.objects.filter(user=request.user).all()
        context = cacu_accuracy(request)
        return render(request, 'user/profile.html', {"results": result_detail, "total_views" : context['total_views'], "accuracy": context['accuracy']})
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def cacu_accuracy(request):
    context = {}
    count_question = ResultDetail.objects.filter(result__user=request.user).count()
    total_answer = ResultDetail.objects.filter(result__user=request.user)

    context['true'] = 0
    context['false'] = 0
    for query_answer in total_answer:
        video = query_answer.video.answer
        answer_result = query_answer.answer
        if video == answer_result:
            context['true'] += 1
        else:
            context['false'] += 1

    accuracy = Decimal(context['true'] * 100 / count_question)
    context = {
        "total_views": count_question,
        "accuracy": accuracy
    }
    return context
