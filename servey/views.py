from django.shortcuts import render, redirect, render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from servey.models import TRAINING_TYPE, TRAINING_LEVEL, ACCURACY_THRESHOLD, CONFIDENCE_LEVEL, EXPERIENCE_NUMBER, UserInfo, Video, Result, ResultDetail
from servey.forms import UserInfoForm
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from decimal import Decimal
from django.conf import settings
from django.template import RequestContext, loader

# Create your views here.


def index(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)

        end_session = False
        all_videos = Video.objects.values_list('id', flat=True)
        latest_result = Result.objects.filter(user=user).order_by('-created_at').first()
        if latest_result is not None:
            exits_video = ResultDetail.objects.filter(result=latest_result).values_list('video_id', flat=True)
            diff = set(all_videos) == set(exits_video)
            if diff:
                end_session = True

        if request.method == 'POST':
            user_exits = Result.objects.filter(user=user, close=False).exists()

            if not user_exits:
                Result.objects.create(user=user,training_type=request.POST['training_type'],accuracy=request.POST['percent'], close=False)
            else:
                Result.objects.filter(user=user).update(
                    training_type=request.POST['training_type'],
                    accuracy=request.POST['percent']
                )
            return redirect('take_the_test')

        user_info = Result.objects.filter(user=user, close=False).order_by('-created_at').first()
        context = {
            'training_type': TRAINING_TYPE,
            'percent': ACCURACY_THRESHOLD,
            "end_session":  end_session
        }

        if user_info is None:
            return render(request, 'servey/index.html', context)
        else:
            question_user = True
            return render(request, 'servey/index.html',{"question_user": question_user})
            # return redirect('take_the_test')
    else:
        return redirect('user_login')


def take_the_test(request):
    if request.user.is_authenticated:
        end_session = False
        user = get_object_or_404(User, pk=request.user.id)

        is_close = Result.objects.filter(user=user, training_type__isnull=False, close=False).order_by('created_at').first()
        if is_close is None:
            return redirect('index')

        all_videos = Video.objects.values_list('id', flat=True)
        latest_result = Result.objects.filter(user=user).order_by('-created_at').first()
        if latest_result is not None:
            exits_video = ResultDetail.objects.filter(result=latest_result).values_list('video_id', flat=True)
            diff = set(all_videos) == set(exits_video)
            if diff:
                end_session = True
            random_video = Video.objects.exclude(id__in=exits_video).order_by('?').first()
        else:
            random_video = Video.objects.order_by('?').first()

        answers = Video.ANSWER_CHOICE
        context = {
            'random_video': random_video,
            'answers': answers,
            'end_session': end_session
        }

        return render(request, 'servey/do_test.html', context)
    else:
        return redirect('index')


@csrf_exempt
def answer_response(request):
    data = {}
    question_id = request.POST['question_id']
    answer = request.POST['answer']
    check = Video.objects.filter(pk=question_id, answer=answer).first()
    check_answer_true = Video.objects.filter(pk=question_id).first()
    answer_true = check_answer_true.get_answer_display()

    exits_user = Result.objects.filter(user=request.user).order_by('-updated_at').first()
    if exits_user.training_type == TRAINING_TYPE[1][1]:
        data['training_type'] = 2
    else:
        data['training_type'] = 1
    if not exits_user:
        result = Result.objects.create(user_id=request.user.id)
        ResultDetail.objects.create(answer=answer, result=result, video_id=question_id)
        check_15 = ResultDetail.objects.filter(result=result)
    else:
        ResultDetail.objects.create(answer=answer, result=exits_user, video_id=question_id)
        check_15 = ResultDetail.objects.filter(result=exits_user).count()

    training_type = Result.objects.filter(user=request.user, training_type=TRAINING_TYPE[1][1], close=False)
    if training_type and check_15 >= 3: #15
        result = Result.objects.filter(user=request.user, close=False).order_by('-updated_at').first()
        accuracy = count_accuracy(result)
        get_accuracy = Decimal(str(accuracy.get('accuracy'))[0:3])
        result_accuracy = result.accuracy
        get_result_accuracy = int(result_accuracy.split("%")[0])
        if get_accuracy >= get_result_accuracy:
            data['congratulation'] = "Congratulations, " + str(get_result_accuracy) + "% accuracy achieved!"
            data['video_viewed'] = accuracy.get("total_video")
            data['overall_accuracy'] = get_accuracy

    end_session = False
    all_videos = Video.objects.values_list('id', flat=True)
    latest_result = Result.objects.filter(user=request.user).order_by('-created_at').first()
    if latest_result is not None:
        exits_video = ResultDetail.objects.filter(result=latest_result).values_list('video_id', flat=True)
        diff = set(all_videos) == set(exits_video)
        if diff:
            end_session = True

    if check is not None:
        data['status'] = True
        data['message'] = "Correct! Ejection fraction is " + answer_true
        data['end_session'] = end_session
        return JsonResponse(data, safe=False)

    else:
        data['status'] = False
        data['message'] = "Incorrect! Ejection fraction is " + answer_true
        data['end_session'] = end_session
        return JsonResponse(data, safe=False)


@login_required(login_url=settings.LOGIN_URL)
def close_test(request):
    exits_user = Result.objects.filter(user=request.user).order_by('-updated_at').first()
    data = {"status": False, "messages": "Test has already been closed"}

    if request.POST and exits_user is not None:
        result_user = Result.objects.filter(user=request.user, close=True)
        if result_user is not None:
            close_result = Result.objects.filter(user=request.user).order_by('-updated_at').first()
            close_result.close = True
            close_result.save()
            return redirect('result_test')
        else:
            return JsonResponse(data, safe=False)
    else:
        return JsonResponse("Method 'GET' not allowed", safe=False)


@login_required(login_url=settings.LOGIN_URL)
def result_test(request):
    result = Result.objects.filter(user=request.user, close=True).order_by('-updated_at').first()
    if result is not None:
        context = {}
        if result.training_type == TRAINING_TYPE[1][1]:
            context['type'] = 2
        context['result_test'] = count_accuracy(result)
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
            # 'institution': request.POST['institution'],
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
            # user_info.institution = form.cleaned_data['institution']
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
        is_admin = User.objects.get(email=email.lower()).is_superuser
        if user is not None:
            login(request, user)
            if is_admin:
                return redirect('admin:index')
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
        context = {}
        count_questions = Video.objects.count()
        count_results = Result.objects.filter(user=request.user).all()
        for result in count_results:
            context[result.id]= count_accuracy(result)
        return render(
            request, 'user/profile.html',
            {
                "count_results": count_results,
                "results": context.items(),
                "count_questions": count_questions
            }
        )
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# statistics
def count_accuracy(result):
    context = {}
    check = ResultDetail.objects.filter(result=result)
    if check is not None:
        count_question = ResultDetail.objects.filter(result=result).count()
        if count_question > 0:
            total_answer = ResultDetail.objects.filter(result=result)

            context['true'] = 0
            context['false'] = 0
            for query_answer in total_answer:
                video = query_answer.video.answer
                answer_result = query_answer.answer
                if video == answer_result:
                    context['true'] += 1
                else:
                    context['false'] += 1

            accuracy = format(Decimal(context['true'] * 100 / count_question), '.2f')
            result_detail = ResultDetail.objects.filter(result=result).values_list('video_id').count()
            context = {
                "date": result.date,
                "total_video": str(context['true']) + "/" + str(result_detail),
                "accuracy": accuracy,
            }
            return context
    else:
        return context


def start_new_session(request):
    if request.method == "POST":
        is_close = Result.objects.filter(user=request.user, close=False).order_by('-updated_at').first()
        if is_close is not None:
            is_close.close = True
            is_close.save()
            return redirect('index')
    else:
        return JsonResponse("Method 'GET' not allowed", safe=False)


@login_required(login_url=settings.LOGIN_URL)
def result_session(request):
    if request.user.is_authenticated:
        total_result = Result.objects.all()
        context = {
            "total_result": total_result,
        }

        return render(request, 'statistical/result_session.html', context)
    else:
        return JsonResponse({"status": False, "messages": "Authentication required"},safe=False)


@login_required(login_url=settings.LOGIN_URL)
def user_account(request):
    if request.user.is_authenticated:
        users = User.objects.filter(is_superuser=False)
        user_info = UserInfo.objects.filter(user__in=users)
        context = {
            "users": user_info
        }
        return render(request, 'statistical/user_account.html', context)
    else:
        return JsonResponse({"status": False, "messages": "Authentication required"},safe=False)


@login_required(login_url=settings.LOGIN_URL)
def video(request):
    if request.user.is_authenticated:
        videos = Video.objects.all()
        context = {
            "videos": videos
        }
        return render(request, 'statistical/video.html', context)
    else:
        return JsonResponse({"status": False, "messages": "Authentication required"},safe=False)


@login_required(login_url=settings.LOGIN_URL)
def detail_video(request, video_pk):
    if request.user.is_authenticated:
        video_detail = get_object_or_404(Video, pk=video_pk)
        count_correct_answer = Video.count_correct_answer_by_level(self=video_pk)
        context = {
            "training_level": TRAINING_LEVEL,
            "video": video_detail,
            "type": count_correct_answer.get("training_type").items(),
            "corect_anwser": count_correct_answer.get("correct_answer").items(),
        }
        return render(request, 'statistical/video_detail.html', context)
    else:
        return JsonResponse({"status": False, "messages": "Authentication required"},safe=False)
