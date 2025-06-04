from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Server
from .serializers import ServerDetailSerializer, ServerSerializer


class ServerList(APIView):
    model_class = Server
    serializer_class = ServerSerializer

    def get(self, request, format=None):
        try:
            query = request.query_params.get("query", "")
            servers = self.model_class.objects.filter(is_active=True)

            if query:
                servers = servers.filter(
                    Q(name__icontains=query) | Q(mini_description__icontains=query)
                ).distinct()

            serializer = self.serializer_class(servers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServerDetail(APIView):
    model_class = Server
    serializer_class = ServerDetailSerializer

    def get(self, request, pk, format=None):
        try:
            server = get_object_or_404(self.model_class, pk=pk, is_active=True)
            serializer = self.serializer_class(server)
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )