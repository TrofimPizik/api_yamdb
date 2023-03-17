import django_filters
from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins, viewsets, permissions, generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from api.permissions import AuthorAccess, ModeratorAccess, AdminAccess, AdminOnly
from api.serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    TitleAddSerializer, ReviewSerializer, CommentSerializer,
    SingUpSerializer, SendTokenSerializer, UserSerializer, 
    UserNotAdminSerializer
)
from reviews.models import Category, Genre, Review, Title
from users.models import User
from api_yamdb.settings import EMAIL_HOST_USER
from rest_framework.views import APIView
from django.db import IntegrityError
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail

class SignUp(APIView):
    """Функция регистрации новых пользователей"""
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetPagination    

    def post(self, request):
        serializer = SingUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get_or_create(
                email=email,
                username=serializer.validated_data['username'],
                is_active=False,
                )[0]
        except IntegrityError as ex:
            if 'UNIQUE constraint failed: reviews_user.username' in ex.args:
                return Response(
                    'username занят', status.HTTP_400_BAD_REQUEST
                )
            return Response(
                'Email занят', status.HTTP_400_BAD_REQUEST
            )                              
        confirmation_code = PasswordResetTokenGenerator().make_token(user)
        send_mail(
            'Добро пожаловать!',
            f'Ваш код подтверждения: {confirmation_code,}',
            EMAIL_HOST_USER,
            [email],
            fail_silently=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)        


class SendToken(APIView):
    """Второй этап регистрации"""
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetPagination    

    def post(self, request):
        serializer = SendTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        try:
            user = get_object_or_404(
                User,
                username=username,
            )
        except User.DoesNotExist:
            return Response('Ошибка в username',
                            status=status.HTTP_404_NOT_FOUND)
        if not PasswordResetTokenGenerator().check_token(user,
                                                         confirmation_code):
            return Response('Неверный код подтверждения',
                            status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user).access_token
        user.is_active = True
        user.save()
        return Response(f'token: {str(token)}', status=status.HTTP_200_OK)


class UserMeViewSet(viewsets.ModelViewSet):
    """Класс для работы с эндпоинтами users"""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, AdminOnly)
    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backend = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = [
        'get', 'post', 'patch', 'delete'
    ]

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes = [permissions.IsAuthenticated],
        url_path='me'
    )
    def get_response_me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            else:
                serializer = UserNotAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()    
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)

class TitleFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', ]


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly & AdminAccess]
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name', ]
    lookup_field = 'slug'


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & AdminAccess]
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name', ]
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly & AdminAccess]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', ]:
            return TitleAddSerializer
        return self.serializer_class


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly & (
            AuthorAccess | ModeratorAccess | AdminAccess
        )
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'),)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'),)
        serializer.save(author=self.request.user, title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly & (
            AuthorAccess | ModeratorAccess | AdminAccess
        )
    ]

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),)
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),)
        serializer.save(author=self.request.user, review_id=review.id)
