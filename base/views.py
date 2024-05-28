from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse, Http404
from .models import Room, Topic ,Message
from .forms import RoomForm, UserForm
from django.utils.decorators import method_decorator

from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views import View  #inheriting base class views built-in
from django.views.generic.list import ListView 
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView , FormMixin , UpdateView , DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .tasks import test_func

   
 
 

class LoginView(View):
    template_name = 'base/login_register.html'
    model = User

    def get(self, request):
        page = "login"
        if request.user.is_authenticated:
            return redirect('home')
        context = {'page': page}
        return render(request, self.template_name, context)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User doesn't exist!")
            return render(request, self.template_name, {'page': 'login'})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist!')
            return render(request, self.template_name, {'page': 'login'})       
        
        
        
        
        

class LogoutView(View):

    # this works same as the redirect
    success_url = 'home' 
    
    def get(self,request):
        logout(request)
        return redirect(self.success_url)

class RegisterPageView(View):
    template_name = 'base/login_register.html'
    success_url = 'home'
    
    def get(self,request):
        form = UserCreationForm
        return render(request,self.template_name,{'form':form})
    
    def post(self,request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            
            login(request,user)
            return redirect(self.success_url)
        
        
        else:
            messages.error(request,"An unxpected error occurred ")
    
        return render(request, self.template_name ,{'form': form})

    
class HomeView(View):
    
    template_name = 'base/home.html'
    
    def get(self,request):
        
        q = request.GET.get('q','')
        
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |  # Q () is used for & , | operations in query
            Q(name__icontains=q) |
            Q(description__icontains=q) 
        
        )

        topics = Topic.objects.all()[0:4] #this is only preview 5 topics by default
        room_count = rooms.count() #logic for showing total rooms
        room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
        
        context = {'rooms': rooms,'topics': topics, 'room_count':room_count, 'room_messages' :room_messages}
        
        return render(request, self.template_name , context)
        


class RoomDetailView(DetailView):
    model = Room
    template_name = 'base/room.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_messages'] = self.object.message_set.all()
        context['participants'] = self.object.participants.all()
        return context

class RoomMessageCreateView(CreateView):
    model = Message
    fields = ['body']
    template_name = 'base/room.html'  # Same template as RoomDetailView

    def form_valid(self, form):
        room = get_object_or_404(Room, id=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.room = room
        form.save()
        room.participants.add(self.request.user)
        return redirect('room', pk=room.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = get_object_or_404(Room, id=self.kwargs['pk'])
        context['room_messages'] = context['room'].message_set.all()
        context['participants'] = context['room'].participants.all()
        return context





class UserProfileView(DetailView):
    
    
    template_name = 'base/profile.html'
    model = User
    context_object_name = 'user'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object 
        context['rooms'] = user.room_set.all()
        context['room_messages'] = user.message_set.all()
        context['topics'] = Topic.objects.all()
        
        return context







# @login_required(login_url='login')
# def createRoom(request):
#     topics = Topic.objects.all()
#     if request.method == 'POST':
#         form = RoomForm(request.POST)
#         if form.is_valid():
#             room = form.save(commit=False)
#             room.host = request.user
#             room.save()
#             return redirect('home')
#         else:
#             context = {'form': form , 'topics': topics}
#             return render(request,'base/room_form.html',context)
#     else:
#         form = RoomForm()
    
#     context = {'form': form , 'topics': topics}
#     return render(request,'base/room_form.html',context)


class CreateRoomView(LoginRequiredMixin,CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'base/room_form.html'
    login_url = 'login'

    
    def get_context_data(self, **kwargs):
       
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all() 
        return context
        
    def form_valid(self, form):
        form.instance.host = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('home')





class RoomUpdateView(UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'base/room_form.html'

    def get_object(self, queryset=None):
        room = super().get_object(queryset)
        if self.request.user != room.host:
            return HttpResponse("You are not allowed here!")
        return room

    def form_valid(self, form):
        topic_name = self.request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = form.save(commit=False)
        room.topic = topic
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        return context





class DeleteRoomView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'base/delete.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return self.model.objects.filter(host=self.request.user)


class DeleteMessageView(LoginRequiredMixin,DeleteView):
    model = Message
    template_name ="base/delete.html"
    success_url = reverse_lazy('home')
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())
    






class UpdateUserView(LoginRequiredMixin,UpdateView):
    model = User
    form_class = UserForm
    template_name = 'base/update_user.html'
    success_url = reverse_lazy('update_user')  # Use reverse_lazy with the named URL pattern

    def get_object(self, queryset=None): # this gets the current user and updates the data
        return self.request.user
  
    
class TopicsPageView(ListView):
    
    model = Topic
    template_name = 'base/topics.html'
    context_object_name = 'topics'
    
    def get_queryset(self):
        
        q = self.request.GET.get('q','')
        return Topic.objects.filter(name__icontains=q)
    


# celery test view

def test(request):
    test_func.delay()
    return HttpResponse("Done")