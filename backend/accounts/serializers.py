from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User, FamilyGroup


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["role"] = user.role
        token["avatar"] = user.avatar
        if user.family_group:
            token["family_group_id"] = user.family_group.id
            token["family_group_name"] = user.family_group.name
        return token

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("用户名或密码错误")

        data = super().validate(attrs)
        data["user"] = UserSerializer(user).data
        return data


class FamilyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyGroup
        fields = ("id", "name", "created_at")


class UserSerializer(serializers.ModelSerializer):
    family_group = FamilyGroupSerializer(read_only=True)
    family_group_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "role_display",
            "avatar",
            "family_group",
            "family_group_id",
            "is_active",
            "is_staff",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "is_active", "is_staff")
