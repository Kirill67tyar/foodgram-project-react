from http import HTTPStatus

from django.test import TestCase


class RecipesAPITestCase(TestCase):

    def test_list_exists(self):
        """Проверка доступности списка задач."""
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)