from djoser.views import RegistrationView
from djoser.constants import Messages
from rest_framework import validators

"""
Список используемых ссылок

 -- api.urls:
https://stackoverflow.com/questions/66036497/djoser-override-registration

 -- api.views:
https://stackoverflow.com/questions/66036497/djoser-override-registration
https://stackoverflow.com/questions/71735934/djoser-override-perform-create-method-of-class-userviewset






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


"""



