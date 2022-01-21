from django.urls import path

from . import views

urlpatterns = [
    path('sign-up/', views.SignupView.as_view()),
    path('sign-in/', views.SigninView.as_view()),
]
