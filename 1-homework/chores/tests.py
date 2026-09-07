from django.db import connection
from django.test import TestCase


class AppConfigTest(TestCase):
	def test_app_is_installed(self):
		from django.apps import apps

		self.assertTrue(apps.is_installed("chores"))

	def test_database_connection_is_available(self):
		with connection.cursor() as cursor:
			cursor.execute("SELECT 1")
			self.assertEqual(cursor.fetchone()[0], 1)
