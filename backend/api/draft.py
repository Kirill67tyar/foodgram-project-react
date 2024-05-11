from djoser.constants import Messages
from djoser.views import RegistrationView
from rest_framework import validators

# # фронт приложения:
# # http://localhost/

# # спецификацию (доки) API:
# # http://localhost/api/docs/redoc.html

# http://localhost/api/users/subscriptions/
# http://localhost/api/users/2/subscribe/
# http://localhost/api/recipes/{id}/shopping_cart/
# http://127.0.0.1:8000/api/recipes/1/shopping_cart/
# http://127.0.0.1:8000/api/recipes/download_shopping_cart/
# http://127.0.0.1:8000/api/recipes-temprorary/download_shopping_cart/

# ? recipe-hub.ru
# ? recipehub.servebeer.com
# ? http://recipehub.servebeer.com/admin/
# ? https://recipehub.servebeer.com/admin/

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
pk 116
r1 = Recipe.objects.create(name='r1', text='r1-text', author=k2, cooking_time=50, image='asd')
r1.tags.add(t1, t2)
ri1 = RecipeIngredient(recipe=r1, ingredient=i1, amount=24)
ri2 = RecipeIngredient(recipe=r1, ingredient=i2, amount=3)
ri1.save()
ri2.save()

r2 = Recipe.objects.create(name='r2', text='r2-text', author=k2, cooking_time=30, image='asd', )
r2.tags.add(t3)
ri3 = RecipeIngredient(recipe=r2, ingredient=i2, amount=70)
ri3.save()

r3 = Recipe.objects.create(name='r3', text='r3-text', author=k2, cooking_time=30, image='asd', )
r3.tags.add(t3)
ri4 = RecipeIngredient(recipe=r3, ingredient=i2, amount=70)
ri4.save()

k1@ya.ru pk 67 6cd85e145896d327652e2c076e8ca8ef3057bedb
k2@ya.ru pk 68 0cc715c107c643c77cd54d5e41ae940484909051

? =-=-= показать все рецепты, которые добавлены в корзину для конкретного пользователя =-=-=
? order = user.orders.filter(downloaded=False).first()
? Recipe.objects.filter(orders__order=order)



! user.orders.filter(items__recipe=recipe, downloaded=False)
! r1.orders.filter(order__owner=k1, order__downloaded=False)


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



...
location / {
        alias /staticfiles/;
        index  index.html index.htm;
        try_files $uri /index.html;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
      }
      error_page   404              /404.html;
      error_page   500 502 503 504  /50x.html;
      location = /50x.html {
        root   /var/html/frontend/;
      }

      
? сбилдить образ
sudo docker build -t f_backend .

? запустить контейнер
sudo docker run --name f_backend_container --rm -p 8000:8000 f_backend
sudo docker run -p 8000:8000 --rm f_backend

? сбилдить образ
sudo docker exec f_backend_container python manage.py migrate

sudo docker exec f_backend_container python manage.py shell_plus
Ingredient.objects.create(name='Капуста', measurement_unit='кг')
Ingredient.objects.create(name='Оливковое масло', measurement_unit='ст. л.')

Tag.objects.create(name='Завтрак', color='#E26C2D', slug='breakfast')
Tag.objects.create(name='Обед', color='#ba2020', slug='lunch')
Tag.objects.create(name='Ужин', color='#2753ab', slug='dinner')


? сборка фронтенда
sudo docker build -t f_frontend .

? запуск контейнера фронтенда
sudo docker run --rm -it -p 8000:8000 --name taski_frontend_test f_frontend

? запуск docker-compose.production.yml
sudo docker compose -f docker-compose.production.yml up
sudo docker-compose -f docker-compose.production.yml up


sudo docker compose exec backend python manage.py migrate

* ---------------------- ответ
# build env
FROM node:13.12.0-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm install --force

COPY . ./

RUN npm run build

? в compose
command: cp -r /app/build/. /frontend_static/


cd frontend  # В директории frontend...
sudo docker build -t kirillbogomolov7ric/foodgram_frontend .

cd ../backend  # То же в директории backend...
sudo docker build -t kirillbogomolov7ric/foodgram_backend .

cd ../gateway  # ...то же и в gateway
sudo docker build -t kirillbogomolov7ric/foodgram_gateway .

sudo nano /etc/nginx/sites-enabled/default

sudo docker push kirillbogomolov7ric/foodgram_frontend
sudo docker push kirillbogomolov7ric/foodgram_backend
sudo docker push kirillbogomolov7ric/foodgram_gateway


sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/


sudo docker compose -f docker-compose.production.yml up -d
sudo docker compose -f docker-compose.production.yml ps
sudo docker compose -f docker-compose.production.yml exec backend bash
sudo docker compose -f docker-compose.production.yml stop
sudo docker compose -f docker-compose.production.yml down



DOCKER_USERNAME
kirillbogomolov7ric



1 - чистим код от комментов
2 - проверяем, будет ли работать modelserializer для User (наводим порядок в сериалайзерах, удаляем лишние и т.д.)
3 - устанавливаем isort и сортируем импорты
4 - выносим SEKRET_KEY и прочее в .env (см. в китиграмм)
5 - выносим в константы все переменные что нужно
6 - удаляем из гита ненужные папки, заносим в .gitignore
7 - добавляем в админку всё что надо (см. платформу)


sudo docker compose -f docker-compose.doc.yml up






kirillbogomolov7ric/kittygram_frontend   <none>    ca53d0639ac1   5 weeks ago         1.39GB
kirillbogomolov7ric/kittygram_backend    <none>    e97f5c318200   5 weeks ago         1.09GB
kirillbogomolov7ric/kittygram_gateway    <none>    b9fc5eb3ae15   5 weeks ago         142MB
kirillbogomolov7ric/kittygram_frontend   <none>    7089af1b299c   5 weeks ago         1.39GB
kirillbogomolov7ric/kittygram_backend    <none>    3709111a54e6   5 weeks ago         1.09GB
kirillbogomolov7ric/kittygram_gateway    <none>    2503489d36ba   5 weeks ago         142MB
kirillbogomolov7ric/kittygram_backend    <none>    d3ce951621e8   6 weeks ago         1.09GB
kirillbogomolov7ric/kittygram_gateway    <none>    f078b6c2b29f   6 weeks ago         142MB
kirillbogomolov7ric/kittygram_frontend   <none>    cecd6a1de3c8   6 weeks ago         1.39GB


TIME_ERROR_MSG
MAX_VALUE_ID = 9223372036854775807  # 


! =-=-=-=-= for settings =-=-=-=-=
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # временная директрия
FONT_PATH = '/home/kirill/Документы/job/projects/training_proj/yandex-practicum/projects/final_proj/foodgram-project-react/backend/fonts/JetBrainsMono-Regular.ttf'
! =-=-=-=-= for settings =-=-=-=-=



-   All database fields
-   Custom manager attributes
-   class Meta
-   def __str__()
-   def save()
-   def get_absolute_url()
-   Any custom methods
"""



