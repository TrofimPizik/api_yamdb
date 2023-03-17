from rest_framework import serializers
from django.core.validators import RegexValidator

from users.models import User


class SingUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации"""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-+\\z]'
        )]        
    )
    email = serializers.EmailField(required=True, max_length=254)
    
    class Meta:
        
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        """
        Проверяет невозможность создания пользователя с ником 'me'
        """
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        return value


class SendTokenSerializer(serializers.Serializer):
    """Сериализатор для функции предоставления токена."""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-+\\z]'
        )]        
    )
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор данных пользователя и админастратора"""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'bio',
            'email',
            'role',
        )


class UserNotAdminSerializer(serializers.ModelSerializer):
    """Сериализатор данных пользователя"""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'bio',
            'email',
            'role',
        )
        read_only_fields = ('role',)