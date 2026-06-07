from datetime import timedelta

from django.db.models import F, FloatField, Prefetch, Value
from django.db.models.expressions import ExpressionWrapper
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import User, Ride, RideEvent
from .pagination import ResultPagination
from .permissions import IsAdminRole
from .serializers import UserSerializer, RideSerializer, RideEventSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id_user")
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    pagination_class = ResultPagination


class RideEventViewSet(viewsets.ModelViewSet):
    queryset = RideEvent.objects.select_related("id_ride").order_by("-created_at")
    serializer_class = RideEventSerializer
    permission_classes = [IsAdminRole]
    pagination_class = ResultPagination


class RideViewSet(viewsets.ModelViewSet):
    serializer_class = RideSerializer
    permission_classes = [IsAdminRole]
    pagination_class = ResultPagination

    def get_queryset(self):
        last_24_hours = timezone.now() - timedelta(hours=24)

        todays_events_queryset = (
            RideEvent.objects
            .filter(created_at__gte=last_24_hours)
            .order_by("-created_at")
        )

        queryset = (
            Ride.objects
            .select_related("id_rider", "id_driver")
            .prefetch_related(
                Prefetch(
                    "ride_events",
                    queryset=todays_events_queryset,
                    to_attr="todays_ride_events",
                )
            )
        )

        status = self.request.query_params.get("status")
        rider_email = self.request.query_params.get("rider_email")
        sort = self.request.query_params.get("sort")

        if status:
            queryset = queryset.filter(status=status)

        if rider_email:
            queryset = queryset.filter(id_rider__email__iexact=rider_email)

        if sort in ["pickup_time", "-pickup_time"]:
            queryset = queryset.order_by(sort)

        elif sort in ["distance", "-distance"]:
            queryset = self.apply_distance_sort(queryset, sort)

        else:
            queryset = queryset.order_by("id_ride")

        return queryset

    def apply_distance_sort(self, queryset, sort):
        pickup_latitude = self.request.query_params.get("pickup_latitude")
        pickup_longitude = self.request.query_params.get("pickup_longitude")

        if pickup_latitude is None or pickup_longitude is None:
            raise ValidationError(
                {
                    "detail": (
                        "pickup_latitude and pickup_longitude are required "
                        "when sorting by distance."
                    )
                }
            )

        try:
            lat = float(pickup_latitude)
            lng = float(pickup_longitude)
        except ValueError:
            raise ValidationError(
                {
                    "detail": (
                        "pickup_latitude and pickup_longitude must be valid numbers."
                    )
                }
            )

        distance_expression = ExpressionWrapper(
            (
                (F("pickup_latitude") - Value(lat))
                * (F("pickup_latitude") - Value(lat))
            )
            + (
                (F("pickup_longitude") - Value(lng))
                * (F("pickup_longitude") - Value(lng))
            ),
            output_field=FloatField(),
        )

        ordering = "-pickup_distance" if sort == "-distance" else "pickup_distance"

        return queryset.annotate(
            pickup_distance=distance_expression
        ).order_by(ordering)