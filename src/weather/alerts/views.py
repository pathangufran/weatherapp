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
from alerts.utils import notification_response
from alerts.redis_service import AlertRedisService
from common.throttling import AlertThrottle

logger = logging.getLogger(__name__)

class CreateAlert(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [AlertThrottle]
    
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

            AlertRedisService.invalidate_alert_cache(request.user.id)

            alert.save()

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
    throttle_classes = [AlertThrottle]

    def get(self,request):

        city_id = request.query_params.get("city_id")
        alert_type = request.query_params.get("alert_type")
        is_active = request.query_params.get("is_active")

        suffix = f"{city_id or 'all'}:{alert_type or 'all'}:{is_active or 'all'}"

        cache_key = AlertRedisService.build_key(
            prefix="alerts",
            user_id=request.user.id,
            suffix=suffix,
        )

        cached_alert = AlertRedisService.get_data(cache_key)

        if cached_alert:
            return Response(
                {
                    "message": "Alerts fetched successfully.",
                    "source": "redis",
                    "data": cached_alert,
                },
                status=status.HTTP_200_OK,
            )
            
        
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

        AlertRedisService.set_data(cache_key,alerts)

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
    throttle_classes = [AlertThrottle]

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
    throttle_classes = [AlertThrottle]

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

            AlertRedisService.invalidate_alert_cache(request.user.id)

            logger.info(
                "Alert cache invalidated after update. User=%s",
                request.user.username,
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
    throttle_classes = [AlertThrottle]

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

            AlertRedisService.invalidate_alert_cache(request.user.id)

            logger.info(
                "Alert cache invalidated after status change. User=%s",
                request.user.username,
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
    throttle_classes = [AlertThrottle]

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

            AlertRedisService.invalidate_alert_cache(request.user.id)

            logger.info(
                "Alert cache invalidated after delete. User=%s",
                request.user.username,
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
        
class GetNotifications(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        try:
            page = int(request.query_params.get("page",1))
            limit = int(request.query_params.get("limit",10))
            is_read = request.query_params.get("is_read")

            suffix = f"{page}:{limit}:{is_read or "all"}"
            cache_key = AlertRedisService.build_key(
                prefix="notifications",
                user_id=request.user.id,
                suffix=suffix,
            )
            cached_data = AlertRedisService.get_data(cache_key)
            if cached_data:
                logger.info(
                    "Returning notifications from Redis."
                )
                return Response(cached_data,status=status.HTTP_200_OK)
            
            queryset = (
                AlertNotification.objects.select_related(
                    "alert",
                    "alert__city",
                    "weather_record"
                )
                .only(
                    "id",
                    "message",
                    "is_read",
                    "created_at",
                    "alert__city__name",
                    "weather_record__temperature",
                    "weather_record__humidity",
                    "weather_record__pressure",
                    "weather_record__wind_speed",
                    "weather_record__weather"
                )
                .filter(alert__user=request.user)
                .order_by("-created_at")
            )
            if is_read is not None:
                queryset = queryset.filter(is_read=is_read)

            paginator = Paginator(queryset,limit)
            try:
                notifications = paginator.page(page)

            except EmptyPage:
                return Response(
                    {"message": "Invalid page number."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            notification_list = [
                notification_response(notification) for notification in notifications
            ]

            data = {
                "message": "Notifications fetched successfully.",
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "page_size": limit,
                "data": notification_list,
            }

            AlertRedisService.set_data(cache_key,data)

            logger.info(
                "Fetched %s notifications for user %s",
                len(notification_list),
                request.user.username,
            )
            return Response(data,status=status.HTTP_200_OK)
        
        except ValueError:
            return Response(
                {"message": "Invalid page or limit."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch notifications : %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class NotificationDetails(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        try:
            notification_id = request.query_params.get('notification_id')
            
            notification = get_object_or_404(
                AlertNotification.objects.select_related(
                    "alert",
                    "alert__city",
                    "weather_record",
                )
                .only(
                    "id",
                    "message",
                    "is_read",
                    "created_at",
                    "alert__user_id",
                    "alert__city__name",
                    "weather_record__temperature",
                    "weather_record__humidity",
                    "weather_record__pressure",
                    "weather_record__wind_speed",
                    "weather_record__weather",
                ),
                id=notification_id,
                alert__user=request.user
            )
            logger.info(
                "Notification %s fetched successfully for user %s",
                notification.id,
                request.user.username,
            )
            return Response(
                {
                    "message": "Notification fetched successfully.",
                    "data": notification_response(notification),
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch notification %s : %s",
                notification_id,
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class NotificationRead(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self,request):

        try:
            notification_id = request.query_params.get("notification_id")
            
            notification = get_object_or_404(
                AlertNotification.objects.only(
                    "id",
                    "is_read",
                    "alert__user_id",
                ),
                id=notification_id,
                alert__user=request.user,
            )
            if notification.is_read:
                logger.info(
                    "Notification %s is already marked as read by user %s",
                    notification.id,
                    request.user.username,
                )
                return Response(
                    {
                        "message": "Notification is already marked as read.",
                        "data": {
                            "id": notification.id,
                            "is_read": notification.is_read,
                        }
                    },
                    status=status.HTTP_200_OK,
                )
            
            notification.is_read = True

            notification.save(update_fields=["is_read"])

            AlertRedisService.invalidate_notification_cache(request.user.id)

            AlertRedisService.invalidate_unread_cache(request.user.id)

            logger.info(
                "Notification cache invalidated. User=%s",
                request.user.username,
            )
            return Response(
                {
                    "message": "Notification marked as read successfully.",
                    "data": {
                        "id": notification.id,
                        "is_read": notification.is_read,
                    }
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception(
                "Failed to mark notification %s as read: %s",
                notification_id,
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class NotificationAllRead(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self,request):

        try:

            updated_count = (
                AlertNotification.objects.filter(
                    alert__user=request.user,
                    is_read=False
                ).update(is_read=True)
            )

            AlertRedisService.invalidate_notification_cache(request.user.id)

            AlertRedisService.invalidate_unread_cache(request.user.id)
            
            logger.info(
                "Notification cache invalidated after mark-all-read. User=%s",
                request.user.username,
            )
            return Response(
                {
                    "message": "All notifications marked as read successfully.",
                    "updated_count": updated_count,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to mark all notifications as read: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class NotificationDelete(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self,request):

        try:
            notification_id = request.data.get("notification_id")
            
            notification = get_object_or_404(
                AlertNotification.objects.only(
                    "id",
                    "alert__user_id",
                ),
                id=notification_id,
                alert__user=request.user
            )
            logger.info(
                "Deleting notification %s for user %s",
                notification.id,
                request.user.username,
            )

            notification.delete()

            AlertRedisService.invalidate_notification_cache(request.user.id)

            AlertRedisService.invalidate_unread_cache(request.user.id)

            logger.info(
                "Notification cache invalidated after delete. User=%s",
                request.user.username,
            )
            return Response(
                {"message": "Notification deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception(
                "Failed to delete notification %s : %s",
                notification_id,
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class NotificationUnreadCount(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        
        try:
            cached_count = AlertRedisService.get_unread_count(request.user.id)
            if cached_count:
                logger.info(
                    "Unread count served from Redis. User=%s",
                    request.user.username,
                )
                return Response(
                    {
                        "message": "Unread notification count fetched successfully.",
                        "source": "redis",
                        "unread_count": cached_count,
                    },
                    status=status.HTTP_200_OK,
                )
            
            unread_count = (
                AlertNotification.objects.filter(
                    alert__user=request.user,
                    is_read=False
                ).count()
            )

            AlertRedisService.set_unread_count(request.user.id,unread_count)

            logger.info(
                "Unread count cached for user %s",
                request.user.username,
            )
            return Response(
                {
                    "message": "Unread notification count fetched successfully.",
                    "source": "database",
                    "unread_count": unread_count,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch unread notification count: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )