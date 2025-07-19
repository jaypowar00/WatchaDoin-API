from django.urls import path
from . import views

urlpatterns = [
    # AUTHENTICATION
    path('auth/signup', views.user_signup, name='user_signup'),
    path('auth/login', views.user_login, name='user_login'),
    path('auth/logout', views.user_logout, name='user_logout'),
    path('auth/refresh-token', views.refresh_token_view, name='refresh_token'),

    # USER MANAGEMENT
    path('manage/profile', views.user_profile, name='user_profile'),
    path('manage/update', views.user_update, name='user_delete'),
    path('manage/delete', views.user_delete, name='user_delete'),
]

# Some Extra TODOs, far-future-ideas
# Next Common Steps (if relevant):
# 1. Throttling / Rate Limiting
#    - Can use Redis to throttle login attempts per IP or per user.
# 2. Permissions/RBAC (e.g., admin, regular users)
# 3. Email/Password Reset