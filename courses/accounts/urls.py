from django.urls import path
from . import views

urlpatterns = [
    path('reg/', views.registration, name='reg'),
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.profile, name="profile"),
    path("settings/", views.settings_view, name='settings'),
    path("settings/profile", views.settings_profile, name="settings_profile"),
    path("settings/password", views.settings_password, name="settings_password")
]