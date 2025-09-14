from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DetailView

from .forms import ProfileAvatarForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile


class AboutMeView(TemplateView):
    template_name = "myauth/about_me.html"


class AboutMeAvatarUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileAvatarForm
    template_name = "myauth/avatar_update.html"
    success_url = reverse_lazy("myauth:about-me")

    def get_object(self, queryset=None):
        return  self.request.user.profile


class UsersListView(ListView):
    template_name = "myauth/users_list.html"
    queryset = User.objects.all().order_by('username')
    context_object_name = "users"


class UserProfileView(DetailView):
    model = User
    template_name = "myauth/user_profile.html"
    queryset = User.objects.select_related('profile').all()
    context_object_name = "user_obj"


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "myauth/user_update.html"

    def get_user_obj(self):
        return User.objects.select_related('profile').get(pk=self.kwargs['pk'])

    def test_func(self):
        return self.request.user.is_staff or self.request.user == self.get_user_obj()

    def get_context_data(self, user_form, profile_form):
        return {
            "user_form": user_form,
            "profile_form": profile_form,
            "user_obj": self.get_user_obj(),
        }

    def get(self, request, *args, **kwargs):
        user_obj = self.get_user_obj()
        user_form = UserUpdateForm(instance=user_obj)
        profile_form = ProfileUpdateForm(instance=user_obj.profile)
        return render(request, self.template_name, self.get_context_data(user_form, profile_form))

    def post(self, request, *args, **kwargs):
        user_obj = self.get_user_obj()
        user_form = UserUpdateForm(request.POST, instance=user_obj)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_obj.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(reverse("myauth:user-profile", kwargs={"pk": user_obj.pk},))

        return render(request, self.template_name, self.get_context_data(user_form, profile_form))


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")

        return render(request, "myauth/login.html")

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", {"error": "Invalid login credentials!"})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("myauth:login"))


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60 * 2)  # Кеширование на 2 минуты
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")
