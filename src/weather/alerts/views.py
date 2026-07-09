import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from alerts.models import WeatherAlert,AlertNotification
from cities.models import City,UserCity
from django.core.paginator import Paginator,EmptyPage

logger = logging.getLogger(__name__)

class CreateAlert(APIView):

    permission_classes = [IsAuthenticated]
    
    def post(self,request):

        city_id = request.data.get("city_id")
        alert_type = request.data.get("alert_type")
        operator = request.data.get("operator")
        threshold = request.data.get("threshold")

        if not city_id or not alert_type or not operator or not threshold:
            return Response(
                {"message": "all the above fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        city = get_object_or_404(City,id=city_id)

        if not UserCity.objects.filter(user=request.user,city=city):
            logger.warning(
                "User %s attempted to create alert for untracked city %s",
                request.user.username,
                city.name,
            )
            return Response(
                {"message": ("Please add this city to your tracked cities first.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if WeatherAlert.objects.filter(
            user=request.user,
            city=city,
            alert_type=alert_type,
            operator=operator,
            threshold=threshold
        ).exists():
            logger.warning(
                "Duplicate alert attempted by user %s",
                request.user.username,
            )
            return Response(
                {"message": "Alert already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            alert = WeatherAlert.objects.create(
                user=request.user,
                city=city,
                alert_type=alert_type,
                operator=operator,
                threshold=threshold,
            )
            logger.info(
                "Weather alert created successfully. "
                "User=%s City=%s Alert=%s",
                request.user.username,
                city.name,
                alert_type,
            )
        except IntegrityError:
            logger.exception("Duplicate weather alert.")
            return Response(
                {"message": "Alert already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception as exc:
            logger.exception("Unexpected error : %s",exc)
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class GetAlerts(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        city_id = request.query_params.get("city_id")
        alert_type = request.query_params.get("alert_type")
        is_active = request.query_params.get("is_active")
        
        filters = {}
        if city_id:
            filters["city_id"] = city_id
        if is_active:
            filters["is_active"] = is_active
        if alert_type:
            filters["alert_type"] = alert_type

        queryset = WeatherAlert.objects.filter(
            user=request.user).select_related("city").order_by("-created_at")
        
        queryset = queryset.filter(**filters)

        page = int(request.query_params.get("page",1))
        limit = int(request.query_params.get("limit",10))
        paginator = Paginator(queryset,limit)
        try:
            alert_page = paginator.page(page)
        except EmptyPage:
            return Response(
                {"message": "Page not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        alerts = []
        for alert in alert_page:
            data = {
                "id": alert.id,
                "city": alert.city.name,
                "alert_type": alert.alert_type,
                "operator": alert.operator,
                "threshold": alert.threshold,
                "is_active": alert.is_active,
                "created_at": alert.created_at,    
            }
            alerts.append(data)

        logger.info(
            "Fetched %s alerts for user %s",
            len(alerts),
            request.user.username,
        )
        return Response(
            {
                "message": "Alerts fetched successfully.",
                "source": "database",
                "count": len(alerts),
                "data": alerts,
            },
            status=status.HTTP_200_OK,
        )
        
class AlertDetails(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        alert_id = request.query_params.get("alert_id")
        if not alert_id:
            return Response(
                {"message":"Alert id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            alert = get_object_or_404(
                WeatherAlert.objects.select_related("city"),
                user=request.user,
                id=alert_id
            )
        except WeatherAlert.DoesNotExist:
            logger.warning(
                "Alert not found. "
                "User=%s Alert=%s",
                request.user.username,
                alert_id,
            )
            return Response(
                {"message": "Alert not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        response_data = {
            "id": alert.id,
            "city_id": alert.city.id,
            "city": alert.city.name,
            "alert_type": alert.alert_type,
            "operator": alert.operator,
            "threshold": alert.threshold,
            "is_active": alert.is_active,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at,
        }
        logger.info(
            "Alert fetched successfully. "
            "User=%s Alert=%s",
            request.user.username,
            alert.id
        )
        return Response(
            {
                "message":"Alert fetched successfully.",
                "data":response_data    
            },
            status=status.HTTP_200_OK
        )
    
class UpdateAlert(APIView):

    permission_classes = [IsAuthenticated]

    def put(self,request):

        try:
            alert_id = request.data.get("alert_id")

            alert = get_object_or_404(
                WeatherAlert.objects.select_related("city"),
                user=request.user,
                id=alert_id
            )
            alert_type = request.data.get("alert_type")
            operator = request.data.get("operator")
            threshold = request.data.get("threshold")
            is_active = request.data.get("is_active")

            valid_alert_types = {
                choice[0]
                for choice in WeatherAlert.ALERT_TYPE_CHOICES
            }
            if alert_type not in valid_alert_types:
                return Response(
                    {"message": "Invalid alert_type."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            valid_operators = {
                choice[0]
                for choice in WeatherAlert.OPERATOR_CHOICES
            }
            if operator not in valid_operators:
                return Response(
                    {"message": "Invalid operator."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            duplicate = WeatherAlert.objects.filter(
                user=request.user,
                city=alert.city,
                alert_type=alert_type,
                operator=operator,
                threshold=threshold
            ).exclude(id=alert.id).exists()

            if duplicate:
                logger.warning(
                    "Duplicate alert update attempted by user %s",
                    request.user.username,
                )
                return Response(
                    {"message": "Alert already exists."},
                    status=status.HTTP_409_CONFLICT,
                )

            alert.alert_type = alert_type
            alert.operator = operator
            alert.threshold = threshold
            alert.is_active = is_active

            alert.save()

            logger.info(
                "Alert updated successfully. User=%s Alert=%s",
                request.user.username,
                alert.id,
            )
            return Response(
                {
                    "message": "Alert updated successfully.",
                    "data": {
                        "id": alert.id,
                        "city": alert.city.name,
                        "alert_type": alert.alert_type,
                        "operator": alert.operator,
                        "threshold": alert.threshold,
                        "is_active": alert.is_active,
                        "updated_at": alert.updated_at,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except IntegrityError:
            logger.exception("Duplicate alert update.")
            return Response(
                {"message": "Alert already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to update alert %s : %s",
                alert_id,
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class AlertStatus(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self,request):

        try:
            alert_id = request.data.get("alert_id")
            alert = get_object_or_404(
                WeatherAlert.objects.only(
                    "id",
                    "is_active",
                    "updated_at",
                    "user_id",
                ),
                user=request.user,
                id=alert_id
            )

            is_active = request.data.get("is_active")
            if not is_active:
                return Response(
                    {"message":"is_active is required.",},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if alert.is_active == is_active:
                return Response(
                    {"message": "Alert is already in the requested state."},
                    status=status.HTTP_200_OK,
                )
            
            alert.is_active = is_active
            alert.save(update_fields=["is_active","updated_at",])

            logger.info(
                "Alert status updated. User=%s Alert=%s Status=%s",
                request.user.username,
                alert.id,
                alert.is_active
            )
            return Response(
                {
                    "message": "Alert status updated successfully.",
                    "data": {
                        "id": alert.id,
                        "is_active": alert.is_active,
                        "updated_at": alert.updated_at,
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception("Failed to update alert status: %s",exc)
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class DeleteAlert(APIView):
    
    permission_classes = [IsAuthenticated]

    def delete(self,request):

        try:
            alert_id = request.data.get("alert_id")
            if not alert_id:
                return Response(
                    {"message":"alert_id is required.",},
                    status=status.HTTP_400_BAD_REQUEST
                )
            alert = get_object_or_404(
                WeatherAlert.objects.only(
                    "id",
                    "user_id",
                    "city_id",
                    "alert_type",
                ),
                user=request.user,
                id=alert_id
            )
            logger.info(
                "Deleting alert. User=%s Alert=%s",
                request.user.username,
                alert.id,
            )
            
            alert.delete()

            logger.info(
                "Alert deleted successfully. User=%s Alert=%s",
                request.user.username,
                alert_id,
            )
            return Response(
                {"message": "Alert deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception(
                "Failed to delete alert %s : %s",
                alert_id,
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )