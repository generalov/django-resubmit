# coding: utf-8
from django.contrib import admin
from django.db import models
from django_resubmit.widgets import FileWidget

from models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title',)
    formfield_overrides = {
	    models.FileField: {'widget': FileWidget()},
    }


admin.site.register(Topic, TopicAdmin)

