from django.db import models
from user.models import User

# Create your models here.
class Topic(models.Model):
	title   = models.CharField(max_length=255)
	author  = models.ForeignKey(User, on_delete=models.CASCADE)
	date    = models.DateTimeField(auto_now_add=True)
	message = models.TextField(max_length=1000)
	solved  = models.BooleanField(default=False)

	def __str__(self):
		return '"' + self.title + '" by ' + self.author.first_name + ' ' + self.author.last_name


class Comment(models.Model):
	topic   = models.ForeignKey(Topic, on_delete=models.CASCADE)
	author  = models.ForeignKey(User, on_delete=models.CASCADE)
	date    = models.DateTimeField(auto_now_add=True)
	message = models.TextField(max_length=1000)

	def __str__(self):
		return ('"' + self.message +
		        '" by ' + self.author.first_name + ' ' + self.author.last_name +
			    ' on "' + self.topic.title +
			    '" by ' + self.topic.author.first_name + ' ' + self.topic.author.last_name)
