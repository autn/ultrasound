from distutils import version
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from .validators import validate_file_extension
import datetime
from decimal import Decimal
# Create your models here.

TRAINING_TYPE = (
 ('Open training session', 'Open training session'),
 ('Until accuracy threshold achieved', 'Until accuracy threshold achieved')
)

TRAINING_LEVEL = (
 ('Medical student', 'Medical student'),
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
        return ResultDetail.objects.filter(result__user=self.user).count()

    @property
    def accuracy_most_recent(self):
        result_users = Result.objects.filter(user=self.user).order_by('-created_at').first()
        return result_users
