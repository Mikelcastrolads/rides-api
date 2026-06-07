from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RideViewSet, RideEventViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("rides", RideViewSet, basename="rides")
router.register("ride-events", RideEventViewSet, basename="ride-events")

urlpatterns = router.urls