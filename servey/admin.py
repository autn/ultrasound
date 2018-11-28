from django.contrib import admin
import django.contrib.auth.admin
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.contrib.auth.admin import UserAdmin
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
    video_count.short_description = "Clips viewed"
    list_display = ['user', 'video_count', 'accuracy']
    list_filter = ['user', 'accuracy']
    search_fields = ['user']

# admin.site.unregister(auth.models.User)
admin.site.unregister(Group)

admin.site.site_header="Ultrasound trainer"
admin.site.site_title = "Ultrasound"
admin.site.index_title = "Ultrasound Admin"


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    def sessions_completed(self,obj):
        users = User.objects.all()
        return Result.objects.filter(user__in=users, close=True).count()

    def clips_viewed(self,obj):
        users = User.objects.all()
        return ResultDetail.objects.filter(result__user__in=users).count()

    def accuracy_most_recent(self,obj):
        context = {}
        users = User.objects.all()
        count_results = Result.objects.filter(user__in=users).all()
        for result in count_results:
            context[result.id] = count_accuracy(result)

        accuracy = list(context.values())
        return str(accuracy[-1].get("accuracy")) + " %"

    list_display = ['user', 'sessions_completed', 'clips_viewed', 'accuracy_most_recent']
    list_filter = ['user']
    search_fields = ['user']
