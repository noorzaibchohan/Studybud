from django.urls import path  
from . import views 
from .views import LoginView , LogoutView , TopicsPageView , HomeView , RegisterPageView , DetailView
from .views import UserProfileView , RoomDetailView , RoomMessageCreateView , UpdateUserView
from .views import  DeleteRoomView ,  DeleteMessageView, CreateRoomView , RoomUpdateView

urlpatterns = [
    
    path('login/',  LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterPageView.as_view(), name='register'),
    path('', views.HomeView.as_view() , name="home"),
    path('room/<str:pk>/', RoomDetailView.as_view(), name='room'),
    path('room/<str:pk>/message/', RoomMessageCreateView.as_view(), name='room_message_create'),
    path('profile/<str:pk>/',views.UserProfileView.as_view(), name='user_profile'),
    
    
    path('create_room/',views.CreateRoomView.as_view() ,name='create_room'),
    path('update_room/<str:pk>/', views.RoomUpdateView.as_view(), name='update_room'),
  
    path('delete_message/<str:pk>/', views.DeleteMessageView.as_view(), name="delete_message"),
    path('delete-room/<int:pk>/', DeleteRoomView.as_view(), name='delete_room'),
    
    
    path('update_user/', views.UpdateUserView.as_view(), name='update_user'),
    path('topics/',  TopicsPageView.as_view() , name='topics'),
    
    
   path('celery/', views.test,name='test'),
    
    
]