from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import AdminSite
from servey.models import Video, Result, ResultDetail, UserInfo
from servey.views import count_accuracy
# Register your models here.


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    ordering = ('-created_at',)
    

admin.site.unregister(Group)
admin.site.site_header="Ultrasound trainer"
admin.site.site_title = "Ultrasound"
admin.site.index_title = "Ultrasound Admin"

# @admin.register(Result)
# class ResultAdmin(admin.ModelAdmin):
#     def video_count(self, obj):
#         context = {}
#         videos = Video.objects.all().values('id', 'answer')
#         context['true'] = 0
#         video_list = ResultDetail.objects.filter(result_id=obj.id).order_by('result_id')
#         context['true'] = 0
#         for answer_correct in video_list:
#             answer_total = answer_correct.video.answer
#
#             answer_result = answer_correct.answer
#             print(answer_result)
#             if answer_total == answer_result:
#                 context['true'] += 1
#         return str(context.get('true')) + "/" + str(obj.result_detail.count())
#
#     video_count.short_description = "Correct Anwser / Clips viewed"
#     list_display = ['user', 'training_type', 'accuracy']
#     list_filter = ['accuracy', 'training_type']
#     search_fields = ['user']

# @admin.register(UserInfo)
# class UserInfoAdmin(admin.ModelAdmin):
#     def sessions_completed(self,obj):
#         return Result.objects.filter(user__in=[obj.user]).count()
#
#     def clips_viewed(self,obj):
#         return ResultDetail.objects.filter(result__user__in=[obj.user]).count()
#
#     def accuracy_most_recent(self,obj):
#         context = {}
#         users = User.objects.all()
#         count_results = Result.objects.filter(user__in=[obj.user]).all()
#         for result in count_results:
#             context[result.id] = count_accuracy(result)
#
#         accuracy = list(context.values())
#         return str(accuracy[-1].get("accuracy")) + " %"
#
#     list_display = ['user', 'sessions_completed', 'clips_viewed', 'accuracy_most_recent']
#     list_filter = ['user']
#     search_fields = ['user']
