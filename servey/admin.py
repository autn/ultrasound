from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import AdminSite
from servey.models import Video, Result, ResultDetail, UserInfo
from servey.views import count_accuracy
# Register your models here.


# class MyAdminSite(AdminSite):
#     def get_urls(self):
#         urls = super(MyAdminSite, self).get_urls()
#         # Note that custom urls get pushed to the list (not appended)
#         # This doesn't work with urls += ...
#         urls = [
#             url(r'^$', self.admin_view(index))
#         ] + urls
#         return urls
#
# admin_site = MyAdminSite()


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    ordering = ('-created_at',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    def video_count(self, obj):

        context = {}
        videos = Video.objects.all().values('id', 'answer')
        # video_list = ResultDetail.objects.filter(result_id=obj.id)

        context['true'] = 0
        # for is_true in video_list:
        #     if is_true.answer == video_list.video.answer:
        #         context['true'] += 1
        #
        # print(context)

        video_list = ResultDetail.objects.filter(result_id=obj.id).order_by('result_id')
        context['true'] = 0
        for answer_correct in video_list:
            answer_total = answer_correct.video.answer

            answer_result = answer_correct.answer
            print(answer_result)
            if answer_total == answer_result:
                context['true'] += 1

        # print(video_list, videos)
        # # c = Result.objects.filter(user_id=7)
        # for item in b:
        #     print(item)
            # c = ResultDetail.objects.filter(result_id=)

        return str(context.get('true')) + "/" + str(obj.result_detail.count())

    # def correct_anwser(self, obj):
    #     return 1
    video_count.short_description = "Correct Anwser / Clips viewed"
    list_display = ['user', 'training_type', 'accuracy']
    list_filter = ['accuracy', 'training_type']
    search_fields = ['user']
    # change_list_template = 'admin/servey/Result/change_list.html'
    # #
    # # def changelist_view(self, request, extra_context=None):
    # #     video = Video.objects.all()
    # #     extra_context['a'] = video
    # #     print(extra_context)
    # #     return super(ResultAdmin, self).changelist_view(request, extra_context)
    #
    # def changelist_view(self, request, extra_context=None):
    #     response = super().changelist_view(
    #         request,
    #         extra_context=extra_context,
    #     )
    #     try:
    #         qs = response.context_data['cl'].queryset
    #     except (AttributeError, KeyError):
    #         return response
    #     users = User.objects.all()
    #     result = Result.objects.filter(user__in=users).all()
    #     detail = {}
    #     for item in result:
    #         detail = ResultDetail.objects.filter(result=result).count()
    #     print(detail)
    #     # response.context_data['videos'] = detail
    #
    #     return response
    #

# admin.site.unregister(auth.models.User)
admin.site.unregister(Group)
#
admin.site.site_header="Ultrasound trainer"
admin.site.site_title = "Ultrasound"
admin.site.index_title = "Ultrasound Admin"


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    def sessions_completed(self,obj):
        return Result.objects.filter(user__in=[obj.user]).count()

    def clips_viewed(self,obj):
        return ResultDetail.objects.filter(result__user__in=[obj.user]).count()

    def accuracy_most_recent(self,obj):
        context = {}
        users = User.objects.all()
        count_results = Result.objects.filter(user__in=[obj.user]).all()
        for result in count_results:
            context[result.id] = count_accuracy(result)

        accuracy = list(context.values())
        return str(accuracy[-1].get("accuracy")) + " %"

    list_display = ['user', 'sessions_completed', 'clips_viewed', 'accuracy_most_recent']
    list_filter = ['user']
    search_fields = ['user']
