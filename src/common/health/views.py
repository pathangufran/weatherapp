from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
    