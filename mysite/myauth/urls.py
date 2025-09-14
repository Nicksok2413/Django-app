from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    AboutMeView,
    AboutMeAvatarUpdateView,
    RegisterView,
    UsersListView,
    UserProfileView,
    UserProfileUpdateView,
    get_cookie_view,
    get_session_view,
    logout_view,
    set_cookie_view,
    set_session_view,
)

app_name = "myauth"

urlpatterns = [
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("about-me/avatar-update/", AboutMeAvatarUpdateView.as_view(), name="avatar-update"),

    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", logout_view, name="logout"),

    path("register/", RegisterView.as_view(), name="register"),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),

    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),

    path("users/", UsersListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("users/<int:pk>/update/", UserProfileUpdateView.as_view(), name="user-profile-update"),
]
