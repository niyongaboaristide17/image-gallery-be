from django.contrib.auth import logout, authenticate
from django.contrib.auth.password_validation import validate_password, password_changed
from django.core.exceptions import ValidationError
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from django.contrib.auth.models import User
from .models import Verification

from .serializers import UserMiniSerializer
from notifications.email_utils import send_email

from sendgrid import SendGridAPIClient
from django.conf import settings


class UserListViewset(GenericAPIView, ListModelMixin):
    serializer_class = UserMiniSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.none()
    ordering = "-date_joined"
    filter_fields = (
        "id", "email", "username", "is_active", "is_staff")
    search_fields = (
        "id", "first_name", "last_name", "email", )
    ordering_fields = (
        "date_joined", "first_name", "last_name",)

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserDetailViewset(GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    serializer_class = UserMiniSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.none()

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)



class AuthenticationViewset(ViewSet):
	permission_classes = [AllowAny]
	
	def get_permissions(self):
		permission_classes = [AllowAny]
		if self.action == 'logout':
			permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]

	@action(detail=False, methods=['post'], url_path="request-verification-code", name='request_verification_code')
	def request_verification_code(self, request):
		"""
        Request an OTP code for various uses
        """
		username = request.data.get("username")
		filter_params = {
			"username": username
		}
		
		if not bool(filter_params):
			return Response({"detail": "Valid email or is not supplied"}, status=400)
		
		user = User.objects.filter(**filter_params).first()

		if not user:
			return Response({"detail": "User not found"}, status=400)

		if not user.is_active:
			return Response({"detail": "The account is not active"}, status=400)
			
		verification, _ = Verification.objects.get_or_create(
            user=user,
            is_valid=True,
            is_used=False
        )
		
		verification.channel = "EMAIL"
		verification.save()
		subject = "Verfication code"
		email_message = "<p><b>{code}</b> is your verification code</p>".format(
			code=verification.code)

		sg_default_sender = settings.SENDGRID_DEFAULT_SENDER

		emails = [username,]
		send_email(emails, subject, email_message, sg_default_sender)

		return Response(
			{"detail": "Verification code has been sent to {username}.".format(username=username)},
			status=200)


	@action(detail=False, methods=['post'], url_path="verify-otp", name='verify-otp')
	def verify_otp(self, request):

		"""
		Login with username, password and OTP code
		"""
		code = request.data.get("code")
		username = request.data.get("username")

		filter_params = {
			"username": username
		}

		if not bool(filter_params):
			return Response({"detail": "Valid email  is not supplied"}, status=400)

		user = User.objects.filter(**filter_params).first()

		if not user:
			return Response({"detail": "No account found"}, status=400)
		if not user.is_active:
			return Response({"detail": "The account is not active"}, status=400)

		verification = Verification.objects.filter(code=code, is_valid=True, is_used=False, user=user).first()

		if not verification:
			return Response({"detail": "Invalid verification code"}, status=400)

		verification.is_used = True
		verification.save()

		return Response({"detail": "OTP verified"}, status=200)

	@action(detail=False, methods=['post'], url_path="authenticate", name='authenticate')
	def perform__authentication(self, request):

		username = request.data.get("username")
		password = request.data.get("password")

		filter_params = {
			"username": username
		}

		if not bool(filter_params):
			return Response({"detail": "Valid email is not supplied"}, status=400)

		user = User.objects.filter(**filter_params).first()

		if not user:
			return Response({"detail": "No account found"}, status=400)
		if not user.is_active:
			return Response({"detail": "The account is not active"}, status=400)

		user = authenticate(username=username, password=password, request=request)

		if not user:
			return Response({"detail": "Invalid credentials"}, status=400)

		context = {
			"request": request
		}

		data = UserMiniSerializer(user, context=context).data

		token, _ = Token.objects.get_or_create(
			user=user
		)
		data["token"] = token.key

		return Response(data, status=200)

	@action(detail=False, methods=['post'], url_path="verify-change-password", name='verify-change-password')
	def verify_change_password(self, request):

		"""
		Change password with OTP
		"""

		code = request.data.get("code")
		username = request.data.get("username")
		password = request.data.get("password")

		filter_params = {
			"username": username
		}

		if not bool(filter_params):
			return Response({"detail": "Valid email is not supplied"}, status=400)

		user = User.objects.filter(**filter_params).first()

		if not user:
			return Response({"detail": "No account found"}, status=400)
		if not user.is_active:
			return Response({"detail": "The account is not active"}, status=400)

		if not password:
			return Response({"detail": "Password not provided"}, status=400)

		verification = Verification.objects.filter(code=code, is_valid=True, is_used=True, user=user).first()

		if not verification:
			return Response({"detail": "Invalid verification code"}, status=400)

		"""
		Validate password
		"""

		try:
			validate_password(password=password, user=user)
		except ValidationError as e:
			return Response({"detail": str(e)}, status=400)

		user.set_password(password)
		user.save()

		verification.is_valid = False
		verification.is_used = True
		verification.save()

		password_changed(password, user)
		Token.objects.filter(user=user).delete()

		return Response({"detail": "Password has been changed successfully"}, status=200)

	@action(detail=False, methods=['post'], url_path="change-password", name='change-password')
	def change_password(self, request):
		password = request.data.get("password")
		new_password = request.data.get("new_password")

		try:
			validate_password(password=password, user=request.user)
		except ValidationError as e:
			return Response({"detail": str(e)}, status=400)

		request.user.set_password(new_password)
		request.user.save()

		return Response({"detail": "Password is changed"}, status=200)

	@action(detail=False, methods=['post'], url_path="register", name='register')
	def register(self, request):
		password = request.data.pop("password")

		try:
			validate_password(password=password, user=request.user)
		except ValidationError as e:
			return Response({"detail": str(e)}, status=400)

		serializer = UserMiniSerializer(data=request.data, context={'request': request})

		if not serializer.is_valid():
			return Response({"detail": serializer.errors}, status=400)

		user = serializer.save()

		user.set_password(password)
		user.save()

		return Response({"detail": "Your account has been created"}, status=200)
		
	@action(detail=False, methods=['get'], url_path="logout", name='logout')
	def signout(self, request):
		if request.user.is_anonymous:
			return Response({"detail": "You are not allowed to perform this operation"}, status=401)
		Token.objects.filter(user=request.user).delete()
		logout(request)
		return Response({"detail": "Signed out"}, status=200)
