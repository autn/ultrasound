from django.contrib import admin
from servey.models import Video, Result, ResultDetail, UserInfo
from django.contrib.auth.models import User, Group
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
