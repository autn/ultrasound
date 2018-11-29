from distutils import version
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from .validators import validate_file_extension
import datetime
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

    class Meta:
        verbose_name = 'Session Result'
    # def video_viewed(self):
    #     # accuracy = Result.objects.all()
    #     # viewed = None
    #     # for item in accuracy:
    #     #     viewed[item.user_id] = ResultDetail.objects.filter(result=11).count()
    #
    #     return ResultDetail.objects.filter(result=11).count()
    #
    # def video(self, obj):
    #     return ", ".join([
    #         child.name for child in obj.children.all()
    #     ])
    #
    # video.short_description = "video"

        # return self.training_type
    #
    # @property
    # def accuracy_test(self):
    #     print(self.count_video_viewed(self))
    #     return self.count_video_viewed(self)


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

    def __str__(self):
        return self.user

    class Meta:
        verbose_name = 'User Info'
