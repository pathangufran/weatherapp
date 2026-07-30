import logging
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from common.health.services import HealthService

logger = logging.getLogger(__name__)

class HealthCheck(APIView):

    """
    Basic health endpoint.
    Used by load balancers, Docker and Kubernetes.
    """
    authentication_classes = []
    permission_classes = []

    def get(self,request):

        return Response(
            {
                "status":"healthy",
                "timestamp":timezone.now()
            },
            status=status.HTTP_200_OK
        )

class DetailedHealthCheck(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self,request):

        overall_status, checks = HealthService.get_healthy_status()
        logger.info(
            "Health check requested. Status=%s",
            overall_status,
        )

        return Response(
            {
                "status": overall_status,
                "checks": checks,
                "timestamp": timezone.now(),
            },
            status=(
                status.HTTP_200_OK
                if overall_status == "healthy"
                else status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )