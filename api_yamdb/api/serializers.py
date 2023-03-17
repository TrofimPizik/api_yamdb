import datetime as dt

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=False)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(default=None)

    class Meta:
        fields = '__all__'
        model = Title


class TitleAddSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug',
    )
    genre = SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True,
    )
    rating = serializers.IntegerField(default=None)

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        year = dt.date.today().year
        if year < value:
            raise serializers.ValidationError('Проверьте год!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username',)

    class Meta:
        # fields = '__all__'
        fields = ('id', 'author', 'text', 'pub_date', 'score',)
        model = Review
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Review.objects.all(),
        #         fields=('author', 'title'),
        #         message=(
        #             'Нельзя подписаться дважды '
        #             'на одного и того же пользователя.'
        #         ),
        #     )
        # ]


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.PrimaryKeyRelatedField(read_only=True)
    author = SlugRelatedField(read_only=True, slug_field='username',)

    class Meta:
        fields = '__all__'
        model = Comment
