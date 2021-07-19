from django import forms

class TopicForm(forms.Form):
    title   = forms.CharField(label="Your title", max_length=100)
    message = forms.CharField(label="Your message", max_length=1000, widget=forms.Textarea)