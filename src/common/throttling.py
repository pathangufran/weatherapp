from rest_framework.throttling import ScopedRateThrottle

class LoginThrottle(ScopedRateThrottle):
    scope = "login"


class RegisterThrottle(ScopedRateThrottle):
    scope = "register"


class RefreshThrottle(ScopedRateThrottle):
    scope = "refresh"


class WeatherThrottle(ScopedRateThrottle):
    scope = "weather"


class DashboardThrottle(ScopedRateThrottle):
    scope = "dashboard"


class AlertThrottle(ScopedRateThrottle):
    scope = "alerts"