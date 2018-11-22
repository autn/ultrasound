from django.contrib import admin
from servey.models import Video
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

    def save_model(self, request, obj, form, change):
        # custom stuff here
        url = obj.URL
        video_id = url.split("=")
        obj.URL = video_id[1]
        super().save_model(request, obj, form, change)
        # obj.save()

