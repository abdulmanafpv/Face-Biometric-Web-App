from django.contrib import admin
from django.urls import path, include
from test_app import views

urlpatterns = [
    path('', views.index,name="index"),
    path('video_feed', views.video_feed, name='video_feed'),
    path('add_photos', views.add_photos, name='add_photos'),
    path('capturing_photos/<int:emp_id>/', views.capturing_photos, name='capturing_photos'),
    path('registration', views.registration, name='registration'),
    # path('detected', views.detected, name='detected'),
    path('train_model', views.train_model, name='train_model'),
    path('search_result', views.search_result, name='search_result'),
    path('train_data', views.train_data, name='train_data'),



]