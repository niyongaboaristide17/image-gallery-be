import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase, override_settings
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from users.models import User, Verification
from django.utils import timezone
from datetime import datetime


class TestAuthentication(TestCase):
    """
    Test authentication process
    Request verification code: User requests OTP code, when no user, one shall be created
    Login: Login with username and OTP code
    Invalidate OTP: After login, the verification code shall be invalid
    """

    def setUp(self):
        self.user = User(
            username="+111111111111",
            email="email@xyz.com",
            first_name="John",
            last_name="Doe"
        )
        self.user.set_password("Testing@2")
        self.user.save()

        self.verification = Verification(
            user=self.user
        )

        self.verification.save()

        self.client = APIClient()

    def test_request_verification_code(self):
        data = {
            "username": "+111111111111"
        }

        response = self.client.post('/auth/request-verification-code', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().keys()), 1)
        self.assertTrue("detail" in response.json())
        self.assertEqual(Verification.objects.filter(user__username="+111111111111").count(), 1)
        self.assertEqual(User.objects.filter(username="+111111111111").count(), 1)

    def test_login(self):
        data = {
            "username": "+111111111111",
            "password": "Testing@2"
        }

        response = self.client.post("/auth/authenticate", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("token" in response.json())
        self.assertEqual(response.json()['first_name'], "John")
        self.assertEqual(response.json()['last_name'], "Doe")
        self.assertEqual(response.json()['email'], "email@xyz.com")
        self.assertEqual(response.json()['username'], "+111111111111")

    def test_login_with_wrong_password(self):
        data = {
            "username": "+111111111111",
            "password": "Wrong password"
        }

        response = self.client.post("/auth/authenticate", data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "Invalid credentials")

    def test_login_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        data = {
            "username": "+111111111111",
            "password": "Testing@2"
        }

        response = self.client.post("/auth/authenticate", data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "The account is not active")

    def test_login_with_no_user(self):
        self.user.is_active = False
        self.user.save()

        data = {
            "username": "+333333333333",
            "password": "Testing@2"
        }

        response = self.client.post("/auth/authenticate", data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "No account found")

    def test_change_password(self):
        self.verification.is_used = True
        self.verification.save()
        data = {
            "username": self.user.username,
            "code": self.verification.code,
            "password": "Kigali@2022"
        }
        response = self.client.post("/auth/verify-change-password", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['detail'], "Password has been changed successfully")

    def test_change_password_with_invalid_otp(self):
        self.verification.is_valid = False
        self.verification.save()
        data = {
            "username": self.user.username,
            "code": self.verification.code,
            "password": "Kigali@2022"
        }
        response = self.client.post("/auth/verify-change-password", data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "Invalid verification code")

    def test_change_password_with_invalid_user(self):
        data = {
            "username": "wrong@user.com",
            "code": self.verification.code,
            "password": "Kigali@2022"
        }
        response = self.client.post("/auth/verify-change-password", data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "No account found")

    def test_change_password_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        data = {
            "username": self.user.username,
            "code": self.verification.code,
            "password": "Kigali@2022"
        }
        response = self.client.post("/auth/verify-change-password", data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "The account is not active")

    def test_change_password_with_no_password(self):
        data = {
            "username": self.user.username,
            "code": self.verification.code,
        }
        response = self.client.post("/auth/verify-change-password", data=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], "Password not provided")

    def test_change_password_with_invalid_password(self):
        data = {
            "username": self.user.username,
            "code": self.verification.code,
            "password": "test"
        }
        response = self.client.post("/auth/verify-change-password", data=data)

        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        self.client.login(
            username="+111111111111",
            code=self.verification.code,
            password="Testing@2")

        response = self.client.get("/auth/logout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['detail'], "Signed out")

    def test_logout_with_anonymous_user(self):
        response = self.client.get("/auth/logout")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['detail'], "You are not allowed to perform this operation")
