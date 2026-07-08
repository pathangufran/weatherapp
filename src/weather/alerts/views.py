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
        
        
        
        
        
        