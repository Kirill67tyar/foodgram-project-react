from djoser.views import RegistrationView
from djoser.constants import Messages
from rest_framework import validators


# # фронт приложения:
# # http://localhost/

# # спецификацию (доки) API:
# # http://localhost/api/docs/redoc.html

# http://localhost/api/users/subscriptions/
# http://localhost/api/users/2/subscribe/

"""
Список используемых ссылок

 -- api.urls:
https://stackoverflow.com/questions/66036497/djoser-override-registration

 -- api.views:
https://stackoverflow.com/questions/66036497/djoser-override-registration
https://stackoverflow.com/questions/71735934/djoser-override-perform-create-method-of-class-userviewset

 -- api.serializers:
https://stackoverflow.com/questions/73616831/serializer-with-m2m-field-with-through-model-got-attributeerror

 -- users.models:
https://github.com/Kirill67tyar/api_final_yatube/blob/master/yatube_api/posts/models.py


"""






"""
sources:
	https://docs.djangoproject.com/en/4.0/ref/models/querysets/#select-related
	https://docs.djangoproject.com/en/4.0/ref/models/querysets/#prefetch-related
	https://django.fun/tutorials/select_related-i-prefetch_related-v-django/ 


---------------------------------------------------------------------------------------------
Если вкратце то:

	select_related:

		доступна
		 - многие к одному (из дочерней модели) - использует INNER JOIN
		 - один к одному - использует LEFT OUTER JOIN или INNER JOIN

		не доступна
		 - для один ко многим - не доступна (из главной модели)
		 - для многие ко многим - не доступна
		 

	prefetch_related:

		пригодна
		 - для многие ко многим - делает два SQL запроса, 
					связывет их в оперативной памяти
					второй SQL запрос на прокси таблицу с 
					внешними ключами (многие ко многим)
					и в ней он использует INNER JOIN
		 - для один к одному - делает 2 SQL запроса и связывает их в оперативной памяти
		 - для один ко многим (из главной модели) - делает два SQL запроса и связывает их

		непригодна
		 - многие к одному (из дочерней модели) - делает два SQL запроса, 
						причём второй только для первой 
						записи из первого запроса (WHERE id IN (1))

---------------------------------------------------------------------------------------------


from pprint import pprint as pp
from django.db import connection, reset_queries
connection.queries
pp(connection.queries)
reset_queries()

 =-=-= Tag =-=-=
Tag.objects.create(name='Завтрак', color='#E26C2D', slug='breakfast')
Tag.objects.create(name='Обед', color='#ba2020', slug='lunch')
Tag.objects.create(name='Ужин', color='#2753ab', slug='dinner')

=-=-= Ingredient =-=-=
Ingredient.objects.create(name='Капуста', measurement_unit='кг')
Ingredient.objects.create(name='Оливковое масло', measurement_unit='ст. л.')
Ingredient.objects.create(name='Соль', measurement_unit='щепотка')

=-=-= Recipe =-=-=
r1 = Recipe.objects.create(name='r1', text='r1-text', author=k, cooking_time=50, image='asd')
r1.tags.add(t1, t2)
ri1 = RI(recipe=r1, ingredient=i1, amount=24)
ri2 = RI(recipe=r1, ingredient=i2, amount=3)
ri1.save()
ri2.save()

r2 = Recipe.objects.create(name='r2', text='r2-text', author=k, cooking_time=30, image='asd', )
r2.tags.add(t3)
ri3 = RI(recipe=r2, ingredient=i2, amount=70)
ri3.save()



{
  "ingredients": [
    {
      "id": 3,
      "amount": 10
    },
    {
      "id": 1,
      "amount": 15
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string1",
  "text": "string1",
  "cooking_time": 1
}



{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}

"""



