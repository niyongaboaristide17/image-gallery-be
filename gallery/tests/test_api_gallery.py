from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from gallery.models import Gallery


class TestUsersList(TestCase):
    """
    Test users list viewset:
    - List as staff
    - List as regular user
    """

    def setUp(self):
        self.user = User(
            username="+111111111111",
            email="email@xyz.com",
            first_name="John",
            last_name="Doe",
            is_staff=True
        )
        self.user.set_password("Testing@2")
        self.user.save()

        self.gallery = Gallery(
            title="Test gallery",
            created_by=self.user
        )

        self.gallery.save()

        self.client = APIClient()

        self.client.login(
            username="+111111111111",
            code=self.verification2.code,
            password="Testing@2")

    def test_list_gallery(self):
        response = self.client.get(
            f"/galleries")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_gallery(self):
        response = self.client.get(
            f"/galleries/{self.gallery.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "Test gallery")

    def test_create_gallery(self):
        data = {
            "title": "Test gallery 2"
        }

        response = self.client.post(
            "/galleries", data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], "Test gallery 2")
        self.assertEqual(Gallery.objects.count(), 2)

    def test_update_gallery(self):
        data = {
            "title": "Updated"
        }

        response = self.client.patch(
            f"/galleries/{self.gallery.id}", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "Updated")

    def test_delete_gallery(self):
        response = self.client.delete(
            f"/galleries/{self.gallery.id}")

        self.assertEqual(response.status_code, 204)
