from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User, Verification


class TestUsersList(TestCase):
    """
    Test users list viewset:
    - List as staff
    - List as regular user
    """

    def setUp(self):
        self.user1 = User(
            username="+111111111111",
            email="email@xyz.com",
            first_name="John",
            last_name="Doe",
            is_staff=True
        )
        self.user1.set_password("Testing@2")
        self.user1.save()

        self.user2 = User(
            username="+2222222222222",
            email="email@xyz.com",
            first_name="John",
            last_name="Doe"
        )
        self.user2.set_password("Testing@2")
        self.user2.save()

        self.verification = Verification(
            user=self.user1
        )

        self.verification2 = Verification(
            user=self.user2
        )

        self.verification2.save()

        self.client = APIClient()

    def test_list_users_as_admin(self):
        self.client.login(
            username="+111111111111",
            code=self.verification.code,
            password="Testing@2")

        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_list_users(self):
        self.client.login(
            username="+2222222222222",
            code=self.verification2.code,
            password="Testing@2")

        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_list_users_unauthenticated(self):
        self.client.logout()

        response = self.client.get("/users")
        self.assertEqual(response.status_code, 403)


class TestUsersDetail(TestCase):
    """
    Test users detail viewset:
    - Retrieve
    - Update user
    """

    def setUp(self):
        self.user1 = User(
            username="+111111111111",
            email="email@xyz.com",
            first_name="John",
            last_name="Doe",
            is_staff=True
        )
        self.user1.set_password("Testing@2")
        self.user1.save()

        self.user2 = User(
            username="+2222222222222",
            email="email@xyz.com",
            first_name="John",
            last_name="Doe"
        )
        self.user2.set_password("Testing@2")
        self.user2.save()

        self.verification = Verification(
            user=self.user1
        )

        self.verification2 = Verification(
            user=self.user2
        )

        self.verification2.save()

        self.client = APIClient()

    def test_get_user_self(self):
        self.client.login(
            username="+2222222222222",
            code=self.verification2.code,
            password="Testing@2")

        response = self.client.get(f"/users/{self.user2.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.user2.id)

    def test_get_user_unauthorized(self):
        self.client.login(
            username="+2222222222222",
            code=self.verification2.code,
            password="Testing@2")

        response = self.client.get(f"/users/{self.user1.id}")
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        self.client.login(
            username="+2222222222222",
            code=self.verification2.code,
            password="Testing@2")

        data = {
            "first_name": "updated",
            "last_name": "updated",
            "email": "updated@email.com",
        }

        response = self.client.patch(f"/users/{self.user2.id}", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.user2.id)
        self.assertEqual(response.json()['first_name'], "updated")
        self.assertEqual(response.json()['last_name'], "updated")
        self.assertEqual(response.json()['email'], "updated@email.com")
