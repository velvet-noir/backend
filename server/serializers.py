from rest_framework import serializers
from .models import Application, Server, ServerSpecification


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
