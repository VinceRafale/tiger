from django.contrib import admin

from tiger.glass.models import Post


class PostModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()


admin.site.register(Post, PostModelAdmin)
