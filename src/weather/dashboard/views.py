import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboard.services import DashboardService

logger = logging.getLogger(__name__)

class DashboardSummary(APIView):

    permission_classes = [IsAuthenticated]

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