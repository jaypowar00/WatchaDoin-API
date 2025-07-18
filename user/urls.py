from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/signup', views.user_signup, name='user_signup'),
    path('auth/login', views.user_login, name='user_login'),
    path('auth/logout', views.user_logout, name='user_logout'),
    path('auth/refresh-token', views.refresh_token_view, name='refresh_token'),

    # USER MANAGEMENT
    path('manage/profile', views.user_profile, name='user_profile'), #
    # path('manage/update', views.user_delete, name='user_delete'), # TODO 1
    # path('manage/delete', views.user_delete, name='user_delete'), # TODO 2
]

# Some Extra TODOs, far-future-ideas
# Next Common Steps (if relevant):
# 1. Token Blacklisting Logic
#    - On logout, store access_token and/or refresh_token in Redis with TTL.
#    - On each request, check if token is blacklisted.
# 2. Auto-refresh (optional)
#    - Add an endpoint or logic to refresh tokens using refresh_token.
# 3. Throttling / Rate Limiting
#    - Can use Redis to throttle login attempts per IP or per user.
# 4. Permissions/RBAC (e.g., admin, regular users)
# 5. Email/Password Reset