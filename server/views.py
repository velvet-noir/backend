from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



from .models import (
    Application,
    ApplicationServer,
    ApplicationStatus,
    Server,
    ServerSpecification,
)
from .serializers import (
    ApplicationSerializer,
    ServerDetailSerializer,
    ServerSerializer,
    ServerSpecSerializer,
)


class ServerList(APIView):
    model_class = Server
    serializer_class = ServerSerializer

    @swagger_auto_schema(
        operation_summary="Получить список всех серверов",
        responses={200: ServerSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "query",
                openapi.IN_QUERY,
                description="Фильтр по имени или описанию",
                type=openapi.TYPE_STRING,
            ),
        ],
        tags=["servers/"],
    )
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

    @swagger_auto_schema(
        operation_summary="Создать новый сервер",
        request_body=ServerSerializer,
        responses={201: ServerSerializer},
        tags=["servers/"],
    )
    def post(self, request, format=None):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"status": "error", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ServerDetail(APIView):
    model_class = Server
    serializer_class = ServerDetailSerializer

    @swagger_auto_schema(
        operation_summary="Получить один сервер по ID с характеристиками",
        responses={200: ServerDetailSerializer},
        tags=["servers/{id}/"],
    )
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

    @swagger_auto_schema(
        operation_summary="Обновить один сервер по ID",
        request_body=ServerDetailSerializer,
        responses={200: ServerDetailSerializer},
        tags=["servers/{id}/"],
    )
    def put(self, request, pk, format=None):
        try:
            server = get_object_or_404(self.model_class, pk=pk)
            serializer = self.serializer_class(server, data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"status": "error", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Удалить(через статус) один сервер по ID",
        responses={204: "No Content"},
        tags=["servers/{id}/"],
    )
    def delete(self, request, pk, format=None):
        try:
            server = get_object_or_404(self.model_class, pk=pk)
            if not server.is_active:
                return Response(
                    {"detail": "Service already deleted"}, status=status.HTTP_410_GONE
                )

            server.is_active = False
            server.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ServerSpecList(APIView):
    model_class = ServerSpecification
    serializer_class = ServerSpecSerializer

    @swagger_auto_schema(
        operation_summary="Получить список всех характеристик",
        responses={200: ServerSpecSerializer(many=True)},
        tags=["spec/"],
    )
    def get(self, request, format=None):
        try:
            specs = self.model_class.objects.all().select_related("server")

            serializer = self.serializer_class(specs, many=True)

            return Response(
                {
                    "status": "success",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Добавить новую характеристику",
        request_body=ServerSpecSerializer,
        responses={201: ServerSpecSerializer},
        tags=["spec/"],
    )
    def post(self, request, format=None):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"status": "error", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ServerSpecDetail(APIView):
    model_class = ServerSpecification
    serializer_class = ServerSpecSerializer

    @swagger_auto_schema(
        operation_summary="Получить характеристику по ID",
        responses={200: ServerSpecSerializer},
        tags=["spec/{id}/"],
    )
    def get(self, request, pk, format=None):
        try:
            spec = get_object_or_404(self.model_class, pk=pk)
            serializer = self.serializer_class(spec)
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Обновить характеристику по ID",
        request_body=ServerSpecSerializer,
        responses={200: ServerSpecSerializer},
        tags=["spec/{id}/"],
    )
    def put(self, request, pk, format=None):
        try:
            spec = get_object_or_404(self.model_class, pk=pk)
            serializer = self.serializer_class(spec, data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"status": "error", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "error", "detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Удалить характеристику по ID",
        responses={204: "No Content"},
        tags=["spec/{id}/"],
    )
    def delete(self, request, pk, format=None):
        try:
            spec = get_object_or_404(self.model_class, pk=pk)
            spec.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "detail": f"Failed to delete specification: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ApplicationList(APIView):
    model_class = Application
    serializer_class = ApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Получить список всех заявок",
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Фильтр по имени статуса заявки",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ApplicationSerializer(many=True)},
        tags=["app/"],
    )
    def get(self, request, format=None):
        try:
            applications = self.model_class.objects.exclude(
                status__in=[ApplicationStatus.DRAFT, ApplicationStatus.DELETED]
            )

            status_name = request.query_params.get("status")
            if status_name:
                applications = applications.filter(status=status_name)

            serializer = self.serializer_class(applications, many=True)
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ApplicationDetail(APIView):
    model_class = Application
    serializer_class = ApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Получить одну заявку по ID",
        responses={200: ApplicationSerializer},
        tags=["app/{id}/"],
    )
    def get(self, request, pk, format=None):
        try:
            application = get_object_or_404(self.model_class, pk=pk)

            serializer = self.serializer_class(application)
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Модератор меняет статус заявки на accepted/completed/rejected",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["status_id"],
        ),
        responses={200: ApplicationSerializer},
        tags=["app/{id}/"],
    )
    def put(self, request, pk, format=None):
        try:
            application = get_object_or_404(self.model_class, pk=pk)
            new_status = request.data.get("status")

            if new_status not in [
                ApplicationStatus.COMPLETED,
                ApplicationStatus.REJECTED,
            ]:
                return Response(
                    {"detail": "Invalid status. Allowed: COMPLETED or REJECTED."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if application.status == new_status:
                return Response(
                    {
                        "detail": f"The application already has the status '{new_status}'"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            application.status = new_status
            application.save()

            serializer = self.serializer_class(application)
            return Response(
                {
                    "status": "success",
                    "data": serializer.data,
                    "detail": f"The application status has been successfully changed to '{new_status}'",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_summary="Удалить заявку через смену статсуса на 'deleted(удалена)'",
        responses={200: ApplicationSerializer},
        tags=["app/{id}/"],
    )
    def delete(self, request, pk, format=None):
        try:
            application = get_object_or_404(self.model_class, pk=pk)

            if application.status == ApplicationStatus.DELETED:
                return Response(
                    {"detail": "The application has already been marked as deleted"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            application.status = ApplicationStatus.DELETED
            application.save()

            serializer = self.serializer_class(application)
            return Response(
                {
                    "status": "success",
                    "data": serializer.data,
                    "detail": "The application has been successfully marked as deleted",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ApplicationFormed(APIView):
    model_class = Application
    serializer_class = ApplicationSerializer

    @swagger_auto_schema(
        operation_summary="Установить для заявки статус 'formed(сформирована)'",
        responses={200: ApplicationSerializer},
        tags=["app/{id}/formed"],
    )
    def put(self, request, pk, format=None):
        try:
            application = get_object_or_404(self.model_class, pk=pk)

            if application.status == ApplicationStatus.FORMED:
                return Response(
                    {"detail": "The application already has the status of 'Formed'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            application.status = ApplicationStatus.FORMED
            application.save()

            serializer = self.serializer_class(application)
            return Response(
                {
                    "status": "success",
                    "data": serializer.data,
                    "detail": "The application status has been successfully changed to 'Formed'",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ApplicationDeleteServer(APIView):
    @swagger_auto_schema(
        operation_summary="Удаление сервера по ID из заявки",
        responses={204: "No Content"},
        tags=["app/{id}/del/{id}/"],
    )
    def delete(self, request, app_id, server_id, format=None):
        try:
            app_server = get_object_or_404(
                ApplicationServer.objects.select_related("application", "server"),
                application_id=app_id,
                server_id=server_id,
            )

            if app_server.application.status != ApplicationStatus.DRAFT:
                return Response(
                    {
                        "status": "error",
                        "detail": "Удаление сервера возможно только для заявок со статусом DRAFT.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            app_server.delete()
            return Response(
                {
                    "status": "success",
                    "detail": "The server was successfully removed from the application.",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"status": "error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
