from django.contrib import admin

# Register your models here.

from .models import User, Topic, Quiz, Question, Rating

admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Rating)
