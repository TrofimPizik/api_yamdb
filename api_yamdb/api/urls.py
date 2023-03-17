from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet, CommentViewSet, GenreViewSet,
    ReviewViewSet, TitleViewSet, SignUp,
    SendToken, UserMeViewSet
)

v1_router = DefaultRouter()
v1_router.register('users', UserMeViewSet, basename='users')
v1_router.register('categories', CategoryViewSet, basename='categories',)
v1_router.register('genres', GenreViewSet, basename='genres',)
v1_router.register('titles', TitleViewSet, basename='titles',)
v1_router.register(

    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews',
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)


urlpatterns = [
    path('v1/auth/signup/', SignUp.as_view(), name='signup'),
    path('v1/auth/token/', SendToken.as_view(), name='login'),
    path('v1/', include([
        path('', include(v1_router.urls)),
    ])),
]
