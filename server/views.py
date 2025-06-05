import datetime
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from .utils import redis_client

from .models import (
    Application,
    ApplicationServer,
    ApplicationStatus,
    Server,
    ServerSpecification,
)
from .serializers import (
    ApplicationSerializer,
    LoginSerializer,
    ServerDetailSerializer,
    ServerSerializer,
    ServerSpecSerializer,
    UserSerializer,
)


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )


class ServerList(APIView):
    model_class = Server
    serializer_class = ServerSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsModerator()]

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

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsModerator()]

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

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsModerator()]

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

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsModerator()]

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

    permission_classes = [IsModerator]  # Только модераторы

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

    def get_permissions(self):
        if self.request.method == "GET":
            if self.request.user.is_staff or self.request.user.is_superuser:
                return [IsAuthenticated()]
            else:
                return [IsAuthenticated()]
        elif self.request.method == "PUT":
            return [IsModerator()]
        elif self.request.method == "DELETE":
            return [IsAuthenticated()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="Получить одну заявку по ID",
        responses={200: ApplicationSerializer},
        tags=["app/{id}/"],
    )
    def get(self, request, pk, format=None):
        try:
            application = get_object_or_404(self.model_class, pk=pk)

            if not (request.user.is_staff or request.user.is_superuser):
                if application.user_creator != request.user:
                    return Response(
                        {
                            "detail": "You do not have permission to view this application."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

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
            required=["status"],
            properties={"status": openapi.Schema(type=openapi.TYPE_STRING)},
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
        operation_summary="Удалить заявку через смену статуса на 'deleted(удалена)'",
        responses={200: ApplicationSerializer},
        tags=["app/{id}/"],
    )
    def delete(self, request, pk, format=None):
        try:
            application = get_object_or_404(self.model_class, pk=pk)

            if application.user_creator != request.user:
                return Response(
                    {
                        "detail": "You do not have permission to delete this application."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Установить для заявки статус 'formed(сформирована)'",
        responses={200: ApplicationSerializer},
        tags=["app/{id}/formed"],
    )
    def put(self, request, pk, format=None):
        try:
            application = get_object_or_404(self.model_class, pk=pk)

            if application.user_creator != request.user:
                return Response(
                    {
                        "detail": "You do not have permission to change the status of this application."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

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
    permission_classes = [IsAuthenticated]

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

            if app_server.application.user_creator != request.user:
                return Response(
                    {
                        "status": "error",
                        "detail": "You do not have permission to modify this application.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = self.get_serializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         operation_summary="Вход пользователя (логин)",
#         request_body=LoginSerializer,
#         responses={200: "Успешный вход", 401: "Неверные учетные данные"},
#         tags=["auth"],
#     )
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         user = authenticate(
#             request,
#             username=serializer.validated_data["username"],
#             password=serializer.validated_data["password"],
#         )
#         if user is not None:
#             login(request, user)
#             return Response({"detail": "Successfully logged in."})
#         return Response(
#             {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
#         )
class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Вход пользователя (логин)",
        request_body=LoginSerializer,
        responses={200: "Успешный вход", 401: "Неверные учетные данные"},
        tags=["auth"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is not None:
            login(request, user)

            log_key = f"user_login:{user.username}"
            timestamp = datetime.datetime.now().isoformat()
            redis_client.lpush(log_key, timestamp)
            redis_client.ltrim(log_key, 0, 99)
            return Response({"detail": "Successfully logged in."})
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "is_staff": user.is_staff,
            }
        )


class DraftApplicationServerView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Добавить услугу (Server) в черновик заявки (создаст заявку, если её нет)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["server_id"],
            properties={
                "server_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={200: "Application с добавленной услугой"},
        tags=["applic/draft/"],
    )
    def post(self, request):
        user = request.user
        server_id = request.data.get("server_id")

        if not server_id:
            return Response(
                {"detail": "server_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            server = Server.objects.get(pk=server_id, is_active=True)
        except Server.DoesNotExist:
            return Response(
                {"detail": "Service not found or inactive"}, status=status.HTTP_404_NOT_FOUND
            )

        application, created = Application.objects.get_or_create(
            user_creator=user,
            status=ApplicationStatus.DRAFT,
        )

        if ApplicationServer.objects.filter(application=application, server=server).exists():
            return Response(
                {"detail": "Service already added to draft application"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ApplicationServer.objects.create(application=application, server=server)

        serializer = ApplicationSerializer(application)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    
    @swagger_auto_schema(
        operation_summary="Получить черновую заявку текущего пользователя, если есть",
        responses={200: ApplicationSerializer},
        tags=["applic/draft/"],
    )
    def get(self, request):
        user = request.user

        application = Application.objects.filter(
            user_creator=user, status=ApplicationStatus.DRAFT
        ).first()

        if not application:
            return Response(
                {"detail": "No draft application found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ApplicationSerializer(application)
        return Response(
            {"status": "success", "data": serializer.data}, status=status.HTTP_200_OK
        )