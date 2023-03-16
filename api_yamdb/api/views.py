import django_filters
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from api.serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    TitleAddSerializer, ReviewSerializer, CommentSerializer,
)
from reviews.models import Category, Genre, Review, Title


class TitleFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', ]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name', ]
    lookup_field = 'slug'

    def retrieve(self, request, slug=None):
        if request.method != 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, slug=None):
        if request.method != 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name', ]
    lookup_field = 'slug'

    def retrieve(self, request, slug=None):
        if request.method != 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, slug=None):
        if request.method != 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', ]:
            return TitleAddSerializer
        return self.serializer_class


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'),)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'),)
        serializer.save(author_id=self.request.user, title_id=title.id)
        # serializer.save(title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),)
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),)
        serializer.save(author=self.request.user, review_id=review.id)
