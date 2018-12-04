from distutils import version
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.aggregates import Sum, Avg
import collections
from .validators import validate_file_extension
import datetime
from decimal import Decimal
from django.db.models import Count
# Create your models here.

TRAINING_TYPE = (
 ('Open training session', 'Open training session'),
 ('Until accuracy threshold achieved', 'Until accuracy threshold achieved')
)

TRAINING_LEVEL = (
 ('Medical_student', 'Medical student'),
 ('Intern', 'Intern'),
 ('Resident', 'Resident'),
 ('Fellow', 'Fellow'),
 ('Attending', 'Attending'),
 ('APP', 'APP'),
 ('Other', 'Other'),
)

CONFIDENCE_LEVEL = (
 ('Somewhat confident', 'Somewhat confident'),
 ('Not at all confident', 'Not at all confident'),
 ('Moderately confident', 'Moderately confident'),
 ('Very confident', 'Very confident'),
 ('Completely confident', 'Completely confident'),
)

EXPERIENCE_NUMBER = (
 ('None', 'None'),
 ('1-20', '1-20 scans interpreted'),
 ('21-100', '21-100 scans interpreted'),
 ('> 100', '> 100 scans interpreted'),
)

ACCURACY_THRESHOLD = (
 ('70%', '70%'),
 ('80%', '80%'),
 ('90%', '90%'),
 ('95%', '95%'),
)


class Video(models.Model):
    ANSWER_CHOICE = (
        (1, 'Normal'),
        (2, 'Moderately reduced',),
        (3, 'Severely reduced',)
    )

    path = models.FileField(blank=True, verbose_name="Upload video (mp4, mkv)", max_length=255, upload_to='videos/', validators=[validate_file_extension])
    title = models.TextField(blank=True, verbose_name="Title question")
    answer = models.IntegerField(choices=ANSWER_CHOICE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def count_answer(self):
        total_answer = ResultDetail.objects.filter(video_id=self.id).count()
        get_correct_answer = ResultDetail.objects.filter(video_id=self.id).values('answer')

        correct = 0
        for item in get_correct_answer:
            if item.get('answer') == self.answer:
                correct +=1

        context = {
            "total": str(correct) + "/" + str(total_answer),
            "accuracy": format(Decimal(correct *100 / total_answer), '.2f')
        }

        return context

    def count_correct_answer_by_level(self):
        context = {}
        training_type = {}
        type_correct = {}
        result_correct = {}
        level_correct = {}
        user_type = {}

        training_type['Medical_student'] = 0
        training_type['Intern'] = 0
        training_type['Resident'] = 0
        training_type['Fellow'] = 0
        training_type['Attending'] = 0
        training_type['APP'] = 0
        training_type['Other'] = 0

        total_answer = ResultDetail.objects.filter(video_id=self)
        result_detail = ResultDetail.objects.filter(video_id=self).values_list('result__user', flat=True)
        this_answer = Video.objects.filter(pk=self).values_list('answer', flat=True)
        # print(this_answer)
        tra_loi_dung = ResultDetail.objects.filter(video_id=self, answer__in=this_answer).values_list('result__user', flat=True)
        count_tra_loi = ResultDetail.objects.filter(video_id=self, answer__in=this_answer).values_list('result__user', flat=True).count()
        print(count_tra_loi)

        users = UserInfo.objects.all()
        a = {}
        b = {}
        for item in tra_loi_dung:
            print(item)
            for user in users:
                if item == user.user_id:
                    a[item] = Result.objects.filter(user_id__in=item)
        # print(UserInfo.objects.filter(user_id=(first_name__in=[item['first_name'] for item in duplicates])))
        # for key, value in TRAINING_LEVEL:
        #     for i in a.values():
        #         if i.get('training_level') == key:
        #             b[key] =

        # select servey_resultdetail.video_id, count(servey_resultdetail.result_id)
        # from servey_resultdetail
        # inner join servey_result
        #     on servey_resultdetail.result_id = servey_result.id
        # inner join servey_userinfo
        #     on servey_result.user_id = servey_userinfo.user_id
        # inner join servey_video
        #     on servey_resultdetail.video_id = servey_video.id
        #     and servey_resultdetail.answer = servey_video.answer
        # where
        # 	  servey_video.id = 6
        # and
        #     servey_userinfo.training_level = "Intern"
        # group by video_id



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
        # print(context)

        # result_check = {}
        # for query_answer in total_answer:
        #     answer_video = query_answer.video.answer
        #     answer_result = query_answer.answer
        #     result_correct[query_answer.id] = [query_answer.id, answer_video, answer_result]
        #
        # for key, value in result_correct.items():
        #     if value[1] == value[2]:
        #         result_check[value[0]] = True
        #     else:
        #         result_check[value[0]] = False
        #
        # for key, result_id in result_check.items():
        #     type_correct[key] = [ResultDetail.objects.filter(pk=key).values_list('result__user__user_info', flat=True),
        #                          result_id]
        #
        # for item in type_correct.values():
        #     if item[1] is True:
        #         for level in item[0]:
        #             # print(level)
        #             level_correct[level] = UserInfo.objects.filter(pk=level).values_list('training_level', flat=True)

        # print(result_detail)

        for user in result_detail:
            # print(user)
            for key, value in TRAINING_LEVEL:
                if UserInfo.objects.get(user=user).training_level == key:
                    training_type[key] += 1
                user_type[key] = UserInfo.objects.filter(training_level=key).values_list('user_id', flat=True).all()

        # print(user_type)
        #
        # for item in training_type:
        #     print(item)

        context = {
            "training_type": training_type,
            "type_correct": type_correct
        }

        # print(user_type)

        return context


class Result(models.Model):
    user = models.ForeignKey(User, related_name='user_result', on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.utcnow, blank=True)
    close = models.BooleanField(default=False, verbose_name="Test is close?", blank=True)
    training_type = models.CharField(choices=TRAINING_TYPE, blank=True, null=True, max_length=255)
    accuracy = models.CharField(max_length=255, choices=ACCURACY_THRESHOLD, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_user(self):
        return User.objects.get(pk=self.user_id)

    @property
    def total_answer(self):
        return self.result_detail.count()

    @property
    def correct_answer(self):
        is_true = 0
        total_video = Video.objects.values('id', 'answer')
        detail = ResultDetail.objects.filter(result=self).values('video_id', 'answer')
        for video in total_video:
            for b in detail:
                if video.get('id') == b.get('video_id'):
                    diff = video.get('answer') == b.get('answer')
                    if diff:
                        is_true += 1

        return is_true

    @property
    def accuracy_count(self):
        context = {}
        check = ResultDetail.objects.filter(result=self.id)
        if check is not None:
            count_question = ResultDetail.objects.filter(result=self.id).count()
            total_answer = ResultDetail.objects.filter(result=self.id)

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
            return accuracy

    # class Meta:
    #     verbose_name = 'Session Result'


class ResultDetail(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, null=True, related_name='result_detail',)
    video = models.ForeignKey(Video, blank=True, on_delete=models.CASCADE, related_name='video_result')
    answer = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserInfo(models.Model):
    user = models.OneToOneField(User, related_name='user_info', on_delete=models.CASCADE)
    institution = models.TextField(blank=True, null=True, max_length=255)
    training_level =  models.CharField(choices=TRAINING_LEVEL, max_length=255,  blank=True, null=True)
    experience = models.CharField(choices=EXPERIENCE_NUMBER, blank=True, null=True, max_length=255)
    confidence_level = models.CharField(blank=True, choices=CONFIDENCE_LEVEL, max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #
    # def __str__(self):
    #     return self.user

    class Meta:
        verbose_name = 'User Info'

    @property
    def sessions_completed(self):
        return Result.objects.filter(user=self.user_id).count()

    @property
    def get_user(self):
        return self.user

    @property
    def clips_viewed(self):
        context = {}

        total_clips = ResultDetail.objects.filter(result__user=self.user)
        count_question = ResultDetail.objects.filter(result__user=self.user).count()

        context['true'] = 0
        context['false'] = 0
        for query_answer in total_clips:
            video = query_answer.video.answer
            answer_result = query_answer.answer
            if video == answer_result:
                context['true'] += 1
            else:
                context['false'] += 1

        context = {
            "count_question": str(context['true']) + "/" + str(count_question),
            "accuracy": format(Decimal(context['true'] * 100 / count_question), '.2f')
        }
        return context

    @property
    def accuracy_most_recent(self):
        result_users = Result.objects.filter(user=self.user).order_by('-created_at').first()
        return result_users
