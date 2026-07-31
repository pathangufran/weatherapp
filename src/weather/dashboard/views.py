import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboard.services import DashboardService
from common.throttling import DashboardThrottle

logger = logging.getLogger(__name__)

class DashboardSummary(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [DashboardThrottle]

    def get(self,request):

        try:

            summary = DashboardService.get_dashboard_summary(request.user)
            logger.info(
                "Dashboard summary fetched successfully for user %s",
                request.user.username,
            )
            return Response(
                {
                    "message": "Dashboard summary fetched successfully.",
                    "data": summary,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Dashboard summary failed: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class DashboardWeatherAnalytics(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [DashboardThrottle]

    def get(self,request):

        try:
            
            analytics = DashboardService.get_weather_analytics(request.user)
            
            logger.info(
                "Weather analytics fetched successfully for user %s",
                request.user.username,
            )
            return Response(
                {
                    "message": "Weather analytics fetched successfully.",
                    "data": analytics,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch weather analytics: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class WeatherTrends(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [DashboardThrottle]

    def  get(self,request):

        try:

            days = int(request.query_params.get("days",7))

            if days <= 0:
                return Response(
                    {"message": "days must be greater than zero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            trend = DashboardService.get_weather_trend(request.user,days)
            logger.info(
                "Weather trend fetched successfully. User=%s Days=%s",
                request.user.username,
                days,
            )
            return Response(
                {
                    "message": "Weather trend fetched successfully.",
                    "data": trend,
                },
                status=status.HTTP_200_OK,
            )
        
        except ValueError:
            return Response(
                {"message": "Invalid value for days."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch weather trend: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class DashboardCityAnalytics(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [DashboardThrottle]

    def get(self,request):

        try:

            analytics = DashboardService.get_city_analytics(request.user)
            logger.info(
                "City analytics fetched successfully. User=%s",
                request.user.username,
            )
            return Response(
                {
                    "message": "City analytics fetched successfully.",
                    "data": analytics,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch city analytics: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class DashboardAlertAnalytics(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [DashboardThrottle]

    def get(self,request):

        try:
            analytics = DashboardService.get_alert_analytics(request.user)
            logger.info(
                "Alert analytics fetched successfully. User=%s",
                request.user.username,
            )
            return Response(
                {
                    "message": "Alert analytics fetched successfully.",
                    "data": analytics,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch alert analytics: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class DashboardNotificationAnalytics(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [DashboardThrottle]

    def get(self,request):

        try:
            analytics = DashboardService.get_notification_analytics(
                request.user,
            )
            logger.info(
                "Notification analytics fetched successfully. User=%s",
                request.user.username,
            )
            return Response(
                {
                    "message": "Notification analytics fetched successfully.",
                    "data": analytics,
                },
                status=status.HTTP_200_OK,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch notification analytics: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class DashboardActivity(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [DashboardThrottle]

    def get(self,request):
    
        try:
            limit = int(request.query_params.get("limit",10))
            if limit <= 0:
                return Response(
                    {"message": "limit must be greater than zero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            activity = DashboardService.get_recent_activity(
                request.user,limit
            )
            logger.info(
                "Recent activity fetched successfully. User=%s",
                request.user.username,
            )
            return Response(
                {
                    "message": "Recent activity fetched successfully.",
                    "count": len(activity),
                    "data": activity,
                },
                status=status.HTTP_200_OK,
            )
        
        except ValueError:
            return Response(
                {"message": "Invalid limit value."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        except Exception as exc:
            logger.exception(
                "Failed to fetch recent activity: %s",
                exc,
            )
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )