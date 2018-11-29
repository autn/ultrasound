from django.contrib import admin
import django.contrib.auth.admin
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.contrib.auth.admin import UserAdmin
from django.template import context

from servey.models import Video, Result, ResultDetail, UserInfo
from servey.views import count_accuracy
# Register your models here.


# class InlineQuestion(admin.TabularInline):
#     model = Answer


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title']
    ordering = ('-created_at',)
    # inlines = [InlineQuestion]

    # def save_model(self, request, obj, form, change):
    #     # custom stuff here
    #     url = obj.URL
    #     video_id = url.split("=")
    #     obj.URL = video_id[1]
    #     super().save_model(request, obj, form, change)
    #     # obj.save()


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    def video_count(self, obj):
        return obj.result_detail.count()
    video_count.short_description = "Correct Anwser / Clips viewed"
    list_display = ['user', 'video_count', 'training_type', 'accuracy']
    list_filter = ['accuracy', 'training_type']
    search_fields = ['user']
    change_list_template = 'admin/servey/result_change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['some_var'] = 'This is what I want to show'
        return super(ResultAdmin, self).changelist_view(request, extra_context=extra_context)
# admin.site.unregister(auth.models.User)
admin.site.unregister(Group)

# admin.site.site_header="Ultrasound trainer"
# admin.site.site_title = "Ultrasound"
# admin.site.index_title = "Ultrasound Admin"


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    def sessions_completed(self,obj):
        # print(obj)
        # return obj.user_result.count()
        # print(count_results)
        # pass
        # # return count_results.user_result.count()
        # for user in count_results:
        #     context[user.id] = Result.objects.filter(user_id=user.id, close=True).count()
        # return context.values()
        return Result.objects.filter(user__in=[obj.user]).count()



    def clips_viewed(self,obj):
        # pass
        # context = {}
        # users = User.objects.all()
        # for result in count:
        #     context[result] = count_accuracy(result)
        # return context.values()

        # return obj.result_detail.count()
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
