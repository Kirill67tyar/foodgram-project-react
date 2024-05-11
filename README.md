# praktikum_new_diplom
## foodgram-project-react
## https://recipehub.servebeer.com

foodgram-project-react - проект, в котором можно можно создавать, редактировать, скачивать рецепты.
Есть возможность регистрации, авторизации, смены пароля, подписки на других пользователей 
Аутентификация реализована через Djoser.
Пример проекта доступен по адресу `https://recipehub.servebeer.com`

### Пользователи на сайте
```
1. Пользователь с правами администратора

    email: admin-user@ya.ru
    password: alskdjfhg

2. Обычные пользователи

    email: kir@ya.ru
    password: alskdjfhg

    email: kir2@ya.ru
    password: alskdjfhg

    email: kazanova@ya.ru
    password: alskdjfhg
```

### Как запустить проект:

```
1. Клонировать репозиторий и перейти в него в командной строке:
    
   git@github.com:Kirill67tyar/foodgram-project-react.git
   
   cd backend/

2. Cоздать и активировать виртуальное окружение:

   python3 -m venv env

-  Если у вас Linux/macOS:
 
   source env/bin/activate
     
-  Если у вас windows:
 
   source env/scripts/activate

3. Обновить pip

   python3 -m pip install --upgrade pip

4. Установить зависимости из файла requirements.txt:

   pip install -r requirements.txt

5. Выполнить миграции:

   python3 manage.py migrate

6. Запустить проект:

   python3 manage.py runserver
```

### Документация к API:

```
1. Перейти в директорию docs/

   cd docs

2. Запустить docker-compose файл, который будет билдить образ и запускать контейнер с документацией

sudo docker compose -f docker-compose.doc.yml up

3. Документация к API доступна по адресу: http://localhost/api/docs/redoc.html
```

### Запуск docker-compose 
```
1. В корневой директории выполнить команду (если хотите скачать образы из dockerhub)

sudo docker compose -f docker-compose.production.yml up -d

2. Или в корневой директории выполнить команду (если хотите сбилдить скачанные образы)

sudo docker compose up -d
```
