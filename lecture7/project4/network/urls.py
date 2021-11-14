
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_post", views.new_post, name="new_post"),
    path('edit_post/<int:id>', views.edit_post, name='edit_post'),
    path('like_post/<int:id>', views.like_post, name="like_post"),
    path('profile/<str:username>', views.profile, name="profile"),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
