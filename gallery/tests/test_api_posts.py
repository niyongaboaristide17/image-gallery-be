from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from gallery.models import Gallery, Post


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

        f = open("gallery/tests/test_image.png", "rb")

        image = SimpleUploadedFile(
            name="post.jpg", content=f.read(), content_type="image/png"
        )

        self.post = Post(
            gallery=self.gallery,
            created_by=self.user,
            image=image,
            title="Test Post",
            description="Test Post description"
        )

        self.post.save()

        self.client = APIClient()

        self.client.login(
            username="+111111111111",
            code=self.verification2.code,
            password="Testing@2")

    def test_list_post(self):
        response = self.client.get(
            f"/posts")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_post(self):
        response = self.client.get(
            f"/posts/{self.post.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "Test Post")

    def test_create_post(self):
        f = open("gallery/tests/test_image.png", "rb")

        image = SimpleUploadedFile(
            name="post.jpg", content=f.read(), content_type="image/png"
        )
        data = {
            "title": "Test gallery 2",
            "description": "Test",
            "image": image
        }

        response = self.client.post(
            "/posts", data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['title'], "Test gallery 2")
        self.assertEqual(response.json()['description'], "Test")
        self.assertEqual(Post.objects.count(), 2)

    def test_update_post(self):
        data = {
            "title": "Updated"
        }

        response = self.client.patch(
            f"/posts/{self.post.id}", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], "Updated")

    def test_delete_post(self):
        response = self.client.delete(
            f"/posts/{self.post.id}")

        self.assertEqual(response.status_code, 204)
