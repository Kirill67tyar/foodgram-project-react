from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthenticatedAndAuthorOrReadOnly
from api.serializers import (IngredientModelSerializer,
                             RecipeReadModelSerializer,
                             RecipeToFavoriteModelSerializer,
                             RecipeWriteModelSerializer, TagModelSerializer,
                             UserSubscriptionsModelSerializer, UserAuthorSubscribeSerializer, AddToFavoriteSerializer)
from orders.models import RecipeOrder
from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.prefetch_related('following')
        elif self.action == 'subscriptions':
            user = self.request.user
            queryset = user.following.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return djoser_settings.SERIALIZERS.user
        if self.action in ('subscriptions',):
            return UserSubscriptionsModelSerializer
        if self.action in ('subscribe',):
            return UserAuthorSubscribeSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get', ],
        url_path='subscriptions',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscriptions(self, request):
        return self.list(request)

    @action(
        detail=True,
        methods=['post',],
        url_path='subscribe',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscribe(self, request, id):
        user = request.user
        serializer = self.get_serializer(
            context={
                'request': request,
                'user': user,
                'user_to_follow': self.get_object(),
            },
            data={'user_to_follow': int(id), }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        serializer = UserAuthorSubscribeSerializer(
            context={
                'request': request,
                'user': user,
                'user_to_follow': self.get_object(),
            },
            data={'user_to_follow': int(id), }
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagReadOnlyModelViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagModelSerializer
    pagination_class = None


class IngredientReadOnlyModelViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientModelSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    filterset_fields = ('name',)


class RecipeModelViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedAndAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = (
        'author',
        'tags',
    )

    queryset = Recipe.objects.select_related(
        'author',
    ).prefetch_related(
        'tags',
        'ingredients',
        'recipeingredient_set__ingredient',
        'author__following',
    )
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]

    def get_object(self):
        if (self.action in ('shopping_cart', 'favorite',)
                and self.request.method == 'POST'):
            queryset = self.filter_queryset(self.get_queryset())
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            recipe = queryset.filter(**filter_kwargs).first()
            if not recipe:
                err_msg = {'Ошибка': 'рецепт отсутствует'}
                raise ValidationError(err_msg)
        return super().get_object()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadModelSerializer
        elif self.action in ('favorite', 'shopping_cart', ):
            return RecipeToFavoriteModelSerializer
            # return AddToFavoriteSerializer
        return RecipeWriteModelSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=[
            'post',
            # 'delete'
        ],
        url_path='favorite',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def favorite(self, request, pk):
        # serializer = self.get_serializer(
        serializer = AddToFavoriteSerializer(
            context={
                'request': request, },
            data={
                'user': request.user.id,
                'recipe': int(pk),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        serializer = AddToFavoriteSerializer(
            context={
                'request': request, },
            data={
                'user': request.user.id,
                'recipe': int(pk),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)

        # user = request.user
        # recipe = self.get_object()
        # if recipe:
        #     recipe_in_favorite = user.favorites.filter(
        #         favorite__recipe=recipe).exists()
        #     if request.method == 'POST':
        #         if not recipe_in_favorite:
        #             user.favorites.add(recipe)
        #             serializer = self.get_serializer(
        #                 recipe
        #             )
        #             return Response(
        #                 data=serializer.data,
        #                 status=status.HTTP_201_CREATED)
        #     else:
        #         if recipe_in_favorite:
        #             user.favorites.remove(recipe)
        #             return Response(
        #                 status=status.HTTP_204_NO_CONTENT)
        # return Response(
        #     status=status.HTTP_400_BAD_REQUEST,
        # )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = self.get_object()
        order = user.orders.filter(downloaded=False).first()
        if not order:
            order = user.orders.create()
        recipe_in_order_for_current_user = RecipeOrder.objects.filter(
            recipe=recipe,
            order=order,
        ).first()
        if request.method == 'POST':
            if not recipe_in_order_for_current_user:
                RecipeOrder.objects.create(
                    recipe=recipe,
                    order=order,
                )
                serializer = self.get_serializer(recipe)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            if recipe_in_order_for_current_user:
                recipe_in_order_for_current_user.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                )
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=['get', ],
        url_path='download_shopping_cart',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def download_shopping_cart(self, request):
        user = request.user
        order = user.orders.filter(downloaded=False).first()
        if not order:
            return HttpResponse(status=200)
        recipe_order_lst = order.items.select_related(
            'recipe'
        ).prefetch_related(
            'recipe__recipeingredient_set__ingredient'
        )
        data = {}
        for r_o in recipe_order_lst:
            for i in r_o.recipe.recipeingredient_set.all():
                key = (i.ingredient.name, i.ingredient.measurement_unit,)
                data[key] = data.get(key, 0) + i.amount

        data_for_output = [
            [k[0], f'{v} {k[-1]}']
            for k, v in data.items()
        ]
        data_for_output.insert(0, ['Ингредиенты', 'Количество', ])

        response = HttpResponse(content_type='application/pdf')
        filename = f'attachment; filename="Заказ-{order.pk}.pdf"'
        response['Content-Disposition'] = filename
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Регистрируем шрифт
        pdfmetrics.registerFont(
            TTFont(django_settings.FONT_NAME, django_settings.FONT_PATH))

        # Создаем таблицу и задаем стиль
        table = Table(
            data_for_output,
            colWidths=250,
            rowHeights=30,
        )
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, -1),
                             django_settings.FONT_NAME),
                            ('FONTSIZE', (0, 0), (-1, -1), 12),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table.setStyle(style)

        # Добавляем таблицу в документ
        elements = [table]
        doc.build(elements)
        order.downloaded = True
        order.save()

        return response
