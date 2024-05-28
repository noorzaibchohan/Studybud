from django import forms
from django.forms import ModelForm
from .models import Room ,Topic
from django.contrib.auth.models import User 


class RoomForm(ModelForm):
    topic = forms.CharField()
    
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host','participants']
        
    def clean_topic(self):
        topic_name = self.cleaned_data.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        return topic
    
        
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username','email',]
        