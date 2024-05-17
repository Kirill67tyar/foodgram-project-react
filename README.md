## foodgram-project-react 
#### https://recipehub.servebeer.com

## Описание проекта

foodgram-project-react - проект, специализирующийся на создавании, и просмотре рецептов. В нём вы можете не только посмотреть чужие рецепты, но и после регистрации, выложить свой в открытый доступ. Можно также скачивать рецепты в удобном PDF формате, где суммируются все ингредиенты, необходимые для списка рецептов, который вы скачали.
Есть возможность регистрации, авторизации, смены пароля, подписки на других пользователей. Также вам будет доступен функционал для добавления рецепта в избранное. Также есть возможность удалять рецепты из избранного и корзины, отписываться от пользователей, а также редактировать и удалять те рецепты, которые вы сами создали.

#### Сайт доступен по адресу: 
https://recipehub.servebeer.com

## Инструкция как развернуть в докере

У вам есть возможность развернуть проект в Docker через конфиг для Docker Compose. Вы можете воспользоваться файлом docker-compose.production.yml и скачать готовые образы из dockerhub, или docker-compose.yml и собрать образы локально в директориях проекта.
```
1. Клонируйте репозиторий к себе на компьютер

   git clone git@github.com:Kirill67tyar/foodgram-project-react.git
   
   или

   git clone https://github.com/Kirill67tyar/foodgram-project-react.git

2. Находясь в корневой директории проекта введите команду, если хотите скачать образы из Dockerhub:

   sudo docker compose -f docker-compose.production.yml up

3. Или если хотите собрать образы локально в директориях проекта:

   sudo docker compose up

4. Проверьте, что все нужные контейнеры запущены (должны быть запущены контейнеры):

   sudo docker compose -f docker-compose.production.yml ps

5. После того как проект развернулся на вашем компьютере, соберите статику django:

   sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic

6. Копируйте статику:

   sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/

7. Примените миграции:

   sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
## Стек технологий

#### для backend:
Python 3.9
PostgreSQL 13
Gunicorn 20.1.0
Nginx 1.22.1

#### для frontend
Node.js 13.12.0

#### для развёртывания на компьютере
Docker 26.1.1
Docker Compose 3

## Как наполнить БД данными
```
   Находясь в корневой директории проекта, после запуска контейнеров через Docker Compose выполните команду (если запускали docker-compose.production.yml):

   sudo docker compose -f docker-compose.production.yml exec backend python manage.py loaddata fixtures/db.json

   sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/fixtures/media/. /media/

или если запускали docker-compose.yml

   sudo docker compose exec backend python manage.py loaddata fixtures/db.json

   sudo docker compose exec backend cp -r /app/fixtures/media/. /media/
```
## Как открыть доку
```
1. Находясь в корневой директории выполните команду:

   cd docs

2. Выполните команду:

   sudo docker compose -f docker-compose.doc.yml up

3. Документация будет развёрнута в контейнере локально и доступна по ссылке:

   http://127.0.0.1:8000/api/docs/redoc.html
```
## Пример запросов/ответов


#####Получить список пользователей:

Request: [GET] http://127.0.0.1:8080/api/api/users/
Response samples:
```
{
  "count": 123,
  "next": "http://127.0.0.1:8080/api/users/?page=4",
  "previous": "http://127.0.0.1:8080/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    }
  ]
}
```
#####Регистрация пользователя:
Request: [POST] http://127.0.0.1:8080/api/users/
Request samples
```
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```
Response samples:
```
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин"
}
```
#####Получить список рецептов:
Request: [GET] http://127.0.0.1:8080/api/recipes/
Response samples:
```
{
  "count": 123,
  "next": "http://127.0.0.1:8080/api/recipes/?page=4",
  "previous": "http://127.0.0.1:8080/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://127.0.0.1:8080/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
```
#####Получить рецепт:
Request: [GET] http://127.0.0.1:8080/api/recipes/{id}/
Response samples:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://127.0.0.1:8080/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```
#####Создание рецепта:
Request: [POST] http://127.0.0.1:8080/api/recipes/{id}/
Request samples
```
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
```
Response samples:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://127.0.0.1:8000/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

## Авторство

#### Backend

Backend разработан [Кирилл Богомолов](https://github.com/Kirill67tyar).

#### Frontend 

Frontend разрабатывала команда [Яндекс Практикум](https://practicum.yandex.ru/python-developer-bootcamp/).
