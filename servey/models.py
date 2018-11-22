from distutils import version

from django.db import models
from django.contrib.auth.models import User
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
 ('Very confident', 'Very confident'),
 ('confident', 'confident'),
 ('somewhat confident', 'somewhat confident'),
 ('somewhat not confident', 'somewhat not confident'),
 ('not confident', 'not confident'),
 ('very not confident', 'very not confident'),
)

EXPERIENCE_NUMBER = (
 ('none', 'none'),
 ('0-10', '0-10'),
 ('11-20', '11-20'),
 ('21-50', '21-50'),
 ('50-100', '50-100'),
 ('> 100', '> 100'),
)

ACCURACY_THRESHOLD = (
 ('70%', '70%'),
 ('80%', '80%'),
 ('90%', '90%'),
 ('95%', '95%'),
)


class Video(models.Model):
    ANSWER_CHOICE = (
        (1, 'Answer_1'),
        (2, 'Answer_2',),
        (3, 'Answer_3',)
    )

    path = models.CharField(blank=True, verbose_name="Path video", max_length=255)
    title = models.TextField(blank=True, verbose_name="Title question")
    answer = models.IntegerField(choices=ANSWER_CHOICE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Result(models.Model):
    user = models.ForeignKey(User, related_name='user_result', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ResultDetail(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, null=True, related_name='result_detail',)
    video = models.OneToOneField(Video, blank=True, on_delete=models.CASCADE)
    answer = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserInfo(models.Model):
    user = models.OneToOneField(User, related_name='user_info', on_delete=models.CASCADE)
    training_type = models.CharField(verbose_name='Training Type', choices=TRAINING_TYPE, blank=True, null=True, max_length=255)
    accuracy = models.CharField(max_length=255, choices=ACCURACY_THRESHOLD, blank=True, null=True)
    institution = models.TextField()
    training_level =  models.CharField(verbose_name='Training level', choices=TRAINING_LEVEL, max_length=255)
    experience = models.CharField(choices=EXPERIENCE_NUMBER, blank=True, null=True, max_length=255)
    confidence_level = models.CharField(blank=True, choices=CONFIDENCE_LEVEL, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)