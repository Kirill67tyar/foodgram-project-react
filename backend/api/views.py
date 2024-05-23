from django.contrib.auth import get_user_model
from django.db.models import Sum
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
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PageNumberWithLimitPagination
from api.permissions import IsAuthenticatedAndAuthorOrReadOnly
from api.serializers import (AddToFavoriteSerializer, AddToShoppingCart,
                             IngredientModelSerializer,
                             RecipeReadModelSerializer,
                             RecipeWriteModelSerializer, TagModelSerializer,
                             UserAuthorSubscribeSerializer,
                             UserSubscriptionsModelSerializer)
from foodgram_backend import constants
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import Follow


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    permission_classes = (AllowAny,)
    pagination_class = PageNumberWithLimitPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'subscriptions':
            user = self.request.user
            queryset = User.objects.filter(from_subscribed__from_user=user)
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
        methods=['post', ],
        url_path='subscribe',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscribe(self, request, id):
        serializer = self.get_serializer(
            data={
                'from_user': request.user.pk,
                'to_user': self.get_object().pk,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        quantity_deleted, _ = Follow.objects.filter(
            from_user=request.user,
            to_user=self.get_object(),
        ).delete()
        if not quantity_deleted:
            raise ValidationError(
                {
                    'errors': constants.MESSAGE_ERROR_DONT_SUBSCRIBE_USER
                }
            )
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
    pagination_class = PageNumberWithLimitPagination
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
    )
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadModelSerializer
        elif self.action in ('favorite', ):
            return AddToFavoriteSerializer
        elif self.action in ('shopping_cart', ):
            return AddToShoppingCart
        return RecipeWriteModelSerializer

    @action(
        detail=True,
        methods=[
            'post',
        ],
        url_path='favorite',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def favorite(self, request, pk):
        serializer = self.get_serializer(
            data={
                'user': request.user.pk,
                'recipe': pk,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        quantity_deleted, _ = Favorite.objects.filter(
            user=request.user,
            recipe=self.get_object(),
        ).delete()
        if not quantity_deleted:
            raise ValidationError(
                {
                    'errors': constants.MESSAGE_ERROR_RECIPE_NOT_IN_FAVORITE
                }
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', ],
        url_path='shopping_cart',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def shopping_cart(self, request, pk):
        serializer = self.get_serializer(
            data={
                'recipes': [pk, ],
                'owner': request.user.pk,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        quantity_deleted, _ = Cart.objects.filter(
            owner=request.user,
            recipes=self.get_object(),
        ).delete()
        if not quantity_deleted:
            raise ValidationError(
                {
                    'errors': constants.MESSAGE_ERROR_RECIPE_NOT_IN_CART
                }
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def generate_pdf_document(self, ingredient_cart_lst, cart):
        data_for_output = [
            [
                ingrdient['name'],
                (f'{ingrdient["total_amount"]} '
                 f'{ingrdient["measurement_unit"]}')
            ]
            for ingrdient in ingredient_cart_lst
        ]

        data_for_output.insert(0, ['Ингредиенты', 'Количество', ])

        response = HttpResponse(content_type='application/pdf')
        filename = f'attachment; filename="Заказ-{cart.pk}.pdf"'
        response['Content-Disposition'] = filename
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Регистрируем шрифт
        pdfmetrics.registerFont(
            TTFont(constants.FONT_NAME, constants.FONT_PATH))

        # Создаем таблицу и задаем стиль
        table = Table(
            data_for_output,
            colWidths=constants.COLWIDTHS_VALUE,
            rowHeights=constants.ROWHEIGHTS_VALUE,
        )
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, -1),
                             constants.FONT_NAME),
                            ('FONTSIZE', (0, 0), (-1, -1), 12),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table.setStyle(style)

        # Добавляем таблицу в документ
        elements = [table]
        doc.build(elements)
        return response

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
        cart = Cart.objects.filter(owner=user).first()
        if not cart:
            return HttpResponse(status=200)
        ingredient_cart_lst = list(Ingredient.objects.filter(
            recipes__carts__owner=user
        ).values(
            'name', 'measurement_unit'
        ).annotate(
            total_amount=Sum('recipeingredient__amount')
        ))
        response = self.generate_pdf_document(
            ingredient_cart_lst,
            cart,
        )
        return response
