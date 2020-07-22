from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login_view", views.login_view, name="login_view"),
    path("logout_view", views.logout_view, name="logout_view"),
    path("profile", views.profile, name="profile"),
    path("leaderboard", views.leaderboard, name="leaderboard"),
]