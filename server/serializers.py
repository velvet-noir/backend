from rest_framework import serializers
from .models import Server, ServerSpecification


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