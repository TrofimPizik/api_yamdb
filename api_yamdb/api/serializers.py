from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
import datetime as dt


from reviews.models import Category, Genre, Title, Review, Comment, GenreTitle


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=False,read_only=True)
    genre = GenreSerializer(many=True,required=False,read_only=True)
    class Meta:
        fields = ('id', 'name', 'year', 'category', 'genre', 'pub_date',)
        model = Title

    
class TitleAddSerializer(serializers.ModelSerializer):
     category = serializers.SlugRelatedField(
         queryset=Category.objects.all(), slug_field='slug',
     )
     genre = serializers.SlugRelatedField(
         queryset=Genre.objects.all(), slug_field='slug', many=True,
     )

     class Meta:
         fields = ('id', 'name', 'year', 'category', 'genre', 'pub_date',)
         model = Title

     def validate_year(self, value):
         year = dt.date.today().year
         if year < value:
             raise serializers.ValidationError('Проверьте год!')
         return value

class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    author = serializers.SlugRelatedField(
        read_only=True, 
        default=serializers.CurrentUserDefault(),
        slug_field='username'
    )
    class Meta:
        fields = ('id', 'title', 'text', 'score', 'author', 'pub_date',)
        model = Review
        read_only_fields = ('author', 'title')
        validators = [
             UniqueTogetherValidator(
                 queryset=Review.objects.all(),
                 fields=('author', 'title'),
                 message=(
                     'Нельзя оставлять оценку дважды '
                     'на одного и тот же фильм.'
                 ),
             )
         ]


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    author = serializers.SlugRelatedField(
        read_only=True, 
        default=serializers.CurrentUserDefault(),
        slug_field='username'
    )
    class Meta:
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('author',)
