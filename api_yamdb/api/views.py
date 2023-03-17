from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import viewsets
from rest_framework import permissions

from api.serializers import SingUpSerializer, SendTokenSerializer, UserSerializer, UserNotAdminSerializer
from users.models import User
from api_yamdb.settings import EMAIL_HOST_USER


class SignUp(APIView):
    """Функция регистрации новых пользователей"""
    serializer_class = SingUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user = User.objects.get_or_create(
            email=email,
            username=serializer.validated_data['username'],
            is_active=False,
            )[0]
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
    permission_classes = [AllowAny]

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
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()