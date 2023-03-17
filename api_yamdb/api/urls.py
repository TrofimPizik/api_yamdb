from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import SignUp, SendToken, UserMeViewSet

router = DefaultRouter()
router.register('users', UserMeViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignUp.as_view(), name='signup'),
    path('v1/auth/token/', SendToken.as_view(), name='login'),
]
