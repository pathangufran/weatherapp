import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from cities.models import *

logger = logging.getLogger(__name__)

class AddCity(APIView):

    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        
        name = request.data.get('name')
        country = request.data.get('country')
        state = request.data.get('state')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if not name or not country or not state or not latitude or not longitude:
            logger.error('All the fields are required')
            return Response(
                {'message':'All the above fields are required'},
                status=status.HTTP_400_BAD_REQUEST    
            )
        try:
            city = City.objects.create(
                name=name,
                country=country,
                state=state,
                latitude=latitude,
                longitude=longitude
            )
            if UserCity.objects.filter(user=request.user,city=city).exists():
                return Response(
                    {"message": "City already added"},
                    status=status.HTTP_409_CONFLICT
                )
            UserCity.objects.create(user=request.user,city=city)
            logger.info('%s added city %s',request.user.username,city.name)
            return Response(
                {
                    'message':'City added successfully',
                    'city_id':city.id,
                    'city_name':city.name 
                },
                status=status.HTTP_201_CREATED    
            )
        except IntegrityError as e:
            logger.error(str(e))
            return Response(
                {'error':'Database error'},
                status=status.HTTP_400_BAD_REQUEST    
            )
        except Exception as e:
            logger.exception(e)
            return Response(
                {'error':'Something went wrong'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR    
            )
        
class GetCity(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        cities = UserCity.objects.filter(user=request.user).select_related('city')
        
        response = []
        for item in cities:
            data = {
                'id':item.city.id,
                'name':item.city.name,
                'country':item.city.country,
                'state':item.city.state,
                'latitude':item.city.latitude,
                'longitude':item.city.longitude
            }
            response.append(data)

        return Response(
            {'count':len(response),'data':response},
            status=status.HTTP_200_OK
        )
    
class DeleteCity(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self,request):

        city_id = request.query_params.get('city_id')
        try:
            user_city = UserCity.objects.select_related('city').get(
                user=request.user,
                city=city_id
            )
            city_name = user_city.city.name
            user_city.delete()
            logger.info(
                '%s removed city %s',
                request.user.username,
                city_name
            )
            return Response(
                {'message':'City deleted successfully'},
                status=status.HTTP_200_OK
            )
        except UserCity.DoesNotExist:
            return Response(
                {'message':'City not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(e)
            return Response(
                {'error':'Something went wrong'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
