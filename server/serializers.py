from rest_framework import serializers
from .models import Application, Server, ServerSpecification
from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"


class ServerSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerSpecification
        fields = "__all__"


class ServerDetailSerializer(serializers.ModelSerializer):
    specifications = ServerSpecSerializer(many=True, read_only=True)

    class Meta:
        model = Server
        fields = [
            "pk",
            "name",
            "image",
            "mini_description",
            "price",
            "is_active",
            "specifications",
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    servers = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "pk",
            "status",
            "created_at",
            "updated_at",
            "user_creator",
            "user_moderator",
            "servers",
        ]

    def get_servers(self, obj):
        app_servers = obj.servers.all()
        servers = [app_server.server for app_server in app_servers]
        return ServerSerializer(servers, many=True).data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "is_staff", "is_superuser"]
        extra_kwargs = {
            "is_staff": {"read_only": True},
            "is_superuser": {"read_only": True},
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError("User with this username already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            is_staff=False,
            is_superuser=False,
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
