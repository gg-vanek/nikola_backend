from django.core.exceptions import ValidationError
from django.test import TestCase
from clients.models import Client


class TaskModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
        # и сохраняем созданную запись в качестве переменной класса
        cls.client = Client.objects.create(
            email='testuser@test.ru',
            first_name='Иван',
            last_name='Иванов',
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        client = TaskModelTest.client

        field_verboses = {
            'email': "Email адрес",
            'first_name': "Имя",
            'last_name': "Фамилия",
            'created_at': "Время создания клиента",
            'updated_at': "Время последнего изменения клиента",
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    client._meta.get_field(field).verbose_name, expected_value)

    def test_unique_client_email(self):
        try:
            client1 = Client.objects.create(
                email="unique_email@test.ru",
                first_name="Иван",
                last_name="Иванов",
            )
            client2 = Client.objects.create(
                email=client1.email,
                first_name="Иван",
                last_name="Иванов",
            )
        except ValidationError:
            client1.delete()
        else:
            client1.delete()
            client2.delete()
            assert False, "Создано 2 клиента с одинаковыми почтами"

    def test_first_name_validators(self):
        for first_name_test_value in ["", "/\\+!@#$%^&*(){}[];:|`~\"\n\t"]:
            try:
                client = Client.objects.create(
                    email="testuser1@test.ru",
                    first_name=first_name_test_value,
                    last_name='Иванов'
                )
            except ValidationError:
                continue
            else:
                client.delete()
                assert False, f'Создан клиент с именем "{first_name_test_value}"'

    def test_last_name_validators(self):
        for last_name_test_value in ["", "/\\+!@#$%^&*(){}[];:|`~\"\n\t"]:
            try:
                client = Client.objects.create(
                    email="testuser1@test.ru",
                    first_name="Иван",
                    last_name=last_name_test_value
                )
            except ValidationError:
                continue
            else:
                client.delete()
                assert False, f'Создан клиент с фамилией "{last_name_test_value}"'

    def test_names_strip(self):
        client = Client.objects.create(
            email='testuser1@test.ru',
            first_name='Иван     ',
            last_name='Иванов   ',
        )
        self.assertEqual(client.first_name, 'Иван')
        self.assertEqual(client.last_name, 'Иванов')
