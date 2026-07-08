from django.db import models
from accounts.models import AuthUser
from cities.models import City
from weatherapp.models import WeatherRecord

class WeatherAlert(models.Model):

    ALERT_TYPE_CHOICES = (

        ("temperature", "Temperature"),
        ("humidity", "Humidity"),
        ("wind_speed", "Wind Speed"),
        ("pressure", "Pressure"),
        ("uv_index", "UV Index"),
        ("condition", "Weather Condition"),

    )

    OPERATOR_CHOICES = (

        ("gt", "Greater Than"),
        ("gte", "Greater Than Equal"),
        ("lt", "Less Than"),
        ("lte", "Less Than Equal"),
        ("eq", "Equal"),

    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AuthUser,on_delete=models.CASCADE,related_name="weather_alerts")
    city = models.ForeignKey(City,on_delete=models.CASCADE,related_name="weather_alerts")
    alert_type = models.CharField(max_length=30,choices=ALERT_TYPE_CHOICES,db_index=True)
    operator = models.CharField(max_length=5,choices=OPERATOR_CHOICES)
    threshold = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        
        db_table = "weather_alert"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user","city"]),
            models.Index(fields=["alert_type","is_active"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "city",
                    "alert_type",
                    "operator",
                    "threshold",
                ],
                name="unique_weather_alert",
            ),
        ]

    def __str__(self):
        return (f"{self.user.username} - " f"{self.city.name} - " f"{self.alert_type}")
    


class AlertNotification(models.Model):

    id = models.AutoField(primary_key=True)
    alert = models.ForeignKey(WeatherAlert,on_delete=models.CASCADE,related_name="notifications")
    weather_record = models.ForeignKey(WeatherRecord,on_delete=models.CASCADE,related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:

        db_table = "alert_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_read","created_at"]),
        ]

    def __str__(self):

        return self.message