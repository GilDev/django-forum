from django.contrib import admin
from .models import Topic, Comment

@admin.display(description='Auteur')
def full_name(obj):
	return obj.author.get_fullname()

@admin.display(description="Topic")
def getTopicTitle(obj):
	return obj.topic.title

# Register your models here.
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
	list_display   = ['title', full_name, 'date', 'solved']
	list_filter    = ['date', 'author__email']
	search_fields  = ['topic', 'message']
	date_hierarchy = 'date'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = [full_name, getTopicTitle, 'date']
	list_filter  = ['date', 'author__email']
	search_fields  = ['message']
	date_hierarchy = 'date'
