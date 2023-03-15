from rest_framework import serializers
import datetime as dt


from reviews.models import Category, Genre, Title, Review, Comment, GenreTitle


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField( 
        slug_field='name',
        queryset=Category.objects.all()
    )
    genre = GenreSerializer(required=False, many=True)
    class Meta:
        fields = ('id', 'name', 'year', 'category', 'genre', 'pub_date')
        model = Title

    def validate_year(self, value):
        year = dt.date.today().year
        if (value > year):
            raise serializers.ValidationError('Проверьте год!')
        return value
    
    def create(self, validated_data):
        if 'genre' not in self.initial_data:
            title = Title.objects.create(**validated_data)
            return title
        
        genres = validated_data.pop('ganre')
        title = Title.objects.create(**validated_data)

        for genre in genres:
            current_genre, status = Genre.objects.get_or_create(
                **genre)
            GenreTitle.objects.create(
                genre_id=current_genre, title_id=title)
        return title 
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.category = validated_data.get('category', instance.category)
        instance.pub_date = validated_data.get(
            'pub_date', instance.pub_date
            )
        if 'genre' in validated_data:
            genres_data = validated_data.pop('genre')
            lst = []
            for genre in genres_data:
                current_genre, status = Genre.objects.get_or_create(
                    **genre
                    )
                lst.append(current_genre)
            instance.genre.set(lst)

        instance.save()
        return instance


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Review.objects.all()
    )
    author = serializers.SlugRelatedField(
        read_only=True, 
        default=serializers.CurrentUserDefault(),
        slug_field='username'
    )
    class Meta:
        fields = ('id', 'title', 'text', 'score', 'author', 'pub_date')
        model = Review
        read_only_fields = ('author', 'title')


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
        read_only_fields = ('author', 'review')
