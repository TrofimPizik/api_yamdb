import django_filters
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from api.serializers import (
     CategorySerializer, GenreSerializer, TitleSerializer, 
     ReviewSerializer, CommentSerializer, TitleAddSerializer
 )
from reviews.models import Category, Genre, Review, Title, Comment
from api.permissions import IsAuthenticated, ReadOnly, IsAuthor


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
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthor | ReadOnly]
    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, 
            title=get_object_or_404(Title, pk=self.kwargs['title_id'])
        )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()
         # serializer.save(title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
     queryset = Comment.objects.all()
     serializer_class = CommentSerializer

     def get_queryset(self):
         review = get_object_or_404(Review, id=self.kwargs.get('review'),)
         return review.comments.all()

     def perform_create(self, serializer):
         review = get_object_or_404(Review, id=self.kwargs.get('review'),)
         serializer.save(author=self.request.user, review_id=review.id)