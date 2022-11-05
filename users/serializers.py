from rest_framework import serializers  
from django.contrib.auth.models import User

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
			"username",
            "email",
            "is_active",
            "is_staff",
        ]
        read_only_fields = ['is_active', 'is_staff',]