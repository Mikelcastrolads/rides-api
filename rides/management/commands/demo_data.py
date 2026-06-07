import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from rides.models import User, Ride, RideEvent


class Command(BaseCommand):
    help = "Create demo users, rides, and ride events"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo rides, ride events, and non-admin users before creating new data.",
        )

        parser.add_argument(
            "--rides",
            type=int,
            default=50,
            help="Number of demo rides to create.",
        )

    def handle(self, *args, **options):
        should_reset = options["reset"]
        ride_count = options["rides"]

        if should_reset:
            self.stdout.write("Removing old demo data...")

            RideEvent.objects.all().delete()
            Ride.objects.all().delete()
            User.objects.exclude(role=User.Role.ADMIN).delete()

        admin_user = self.create_demo_admin()
        riders = self.create_demo_users(role=User.Role.RIDER, count=10)
        drivers = self.create_demo_users(role=User.Role.DRIVER, count=5)

        rides = self.create_demo_rides(
            ride_count=ride_count,
            riders=riders,
            drivers=drivers,
        )

        self.create_demo_ride_events(rides)

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
        self.stdout.write(f"Admin email: {admin_user.email}")
        self.stdout.write("Admin password: admin123")
        self.stdout.write(f"Riders created: {len(riders)}")
        self.stdout.write(f"Drivers created: {len(drivers)}")
        self.stdout.write(f"Rides created: {len(rides)}")

    def create_demo_admin(self):
        admin_user, _ = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "role": User.Role.ADMIN,
                "first_name": "Admin",
                "last_name": "User",
                "phone_number": "09170000000",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.set_password("admin123")
        admin_user.save()

        return admin_user

    def create_demo_users(self, role, count):
        users = []

        first_names = [
            "Juan",
            "Maria",
            "Jose",
            "Ana",
            "Carlo",
            "Rica",
            "Miguel",
            "Angela",
            "Mark",
            "Grace",
        ]

        last_names = [
            "Santos",
            "Reyes",
            "Cruz",
            "Garcia",
            "Dela Cruz",
            "Mendoza",
            "Aquino",
            "Castro",
            "Ramos",
            "Torres",
        ]

        for index in range(1, count + 1):
            email = f"{role}{index}@example.com"

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "role": role,
                    "first_name": first_names[index - 1],
                    "last_name": last_names[index - 1],
                    "phone_number": f"09170000{index:03d}",
                    "is_active": True,
                },
            )

            if created:
                user.set_password("test123")
                user.save()

            users.append(user)

        return users

    def create_demo_rides(self, ride_count, riders, drivers):
        statuses = [
            Ride.Status.EN_ROUTE,
            Ride.Status.PICKUP,
            Ride.Status.DROPOFF,
        ]

        pampanga_locations = [
            {
                "name": "Angeles City",
                "latitude": 15.1449,
                "longitude": 120.5887,
            },
            {
                "name": "City of San Fernando",
                "latitude": 15.0333,
                "longitude": 120.6833,
            },
            {
                "name": "Mabalacat City",
                "latitude": 15.2230,
                "longitude": 120.5799,
            },
            {
                "name": "Apalit",
                "latitude": 14.9533,
                "longitude": 120.7699,
            },
            {
                "name": "Arayat",
                "latitude": 15.1493,
                "longitude": 120.7690,
            },
            {
                "name": "Bacolor",
                "latitude": 15.0000,
                "longitude": 120.6500,
            },
            {
                "name": "Candaba",
                "latitude": 15.0956,
                "longitude": 120.8267,
            },
            {
                "name": "Floridablanca",
                "latitude": 14.9775,
                "longitude": 120.5285,
            },
            {
                "name": "Guagua",
                "latitude": 14.9653,
                "longitude": 120.6325,
            },
            {
                "name": "Lubao",
                "latitude": 14.9405,
                "longitude": 120.6011,
            },
            {
                "name": "Macabebe",
                "latitude": 14.9089,
                "longitude": 120.7155,
            },
            {
                "name": "Magalang",
                "latitude": 15.2151,
                "longitude": 120.6596,
            },
            {
                "name": "Masantol",
                "latitude": 14.8960,
                "longitude": 120.7097,
            },
            {
                "name": "Mexico",
                "latitude": 15.0646,
                "longitude": 120.7198,
            },
            {
                "name": "Minalin",
                "latitude": 14.9676,
                "longitude": 120.6825,
            },
            {
                "name": "Porac",
                "latitude": 15.0711,
                "longitude": 120.5423,
            },
            {
                "name": "San Luis",
                "latitude": 15.0406,
                "longitude": 120.7917,
            },
            {
                "name": "San Simon",
                "latitude": 14.9996,
                "longitude": 120.7808,
            },
            {
                "name": "Santa Ana",
                "latitude": 15.0955,
                "longitude": 120.7671,
            },
            {
                "name": "Santa Rita",
                "latitude": 14.9994,
                "longitude": 120.6151,
            },
            {
                "name": "Santo Tomas",
                "latitude": 14.9923,
                "longitude": 120.7052,
            },
            {
                "name": "Sasmuan",
                "latitude": 14.9445,
                "longitude": 120.6211,
            },
        ]

        rides = []

        for _ in range(ride_count):
            pickup_location = random.choice(pampanga_locations)
            dropoff_location = random.choice(pampanga_locations)

            pickup_latitude = pickup_location["latitude"] + random.uniform(-0.01, 0.01)
            pickup_longitude = pickup_location["longitude"] + random.uniform(-0.01, 0.01)

            dropoff_latitude = dropoff_location["latitude"] + random.uniform(-0.01, 0.01)
            dropoff_longitude = dropoff_location["longitude"] + random.uniform(-0.01, 0.01)

            ride = Ride.objects.create(
                status=random.choice(statuses),
                id_rider=random.choice(riders),
                id_driver=random.choice(drivers),
                pickup_latitude=pickup_latitude,
                pickup_longitude=pickup_longitude,
                dropoff_latitude=dropoff_latitude,
                dropoff_longitude=dropoff_longitude,
                pickup_time=timezone.now()
                + timedelta(minutes=random.randint(-5000, 5000)),
            )

            ride.demo_pickup_name = pickup_location["name"]
            ride.demo_dropoff_name = dropoff_location["name"]

            rides.append(ride)

        return rides

    def create_demo_ride_events(self, rides):
        now = timezone.now()
        events = []

        for ride in rides:
            pickup_created_at = now - timedelta(
                hours=random.randint(1, 72),
                minutes=random.randint(0, 59),
            )

            dropoff_created_at = pickup_created_at + timedelta(
                minutes=random.randint(20, 140)
            )

            pickup_name = getattr(ride, "demo_pickup_name", "Pampanga")
            dropoff_name = getattr(ride, "demo_dropoff_name", "Pampanga")

            events.append(
                RideEvent(
                    id_ride=ride,
                    description="Status changed to pickup",
                    created_at=pickup_created_at,
                )
            )

            events.append(
                RideEvent(
                    id_ride=ride,
                    description="Status changed to dropoff",
                    created_at=dropoff_created_at,
                )
            )

            events.append(
                RideEvent(
                    id_ride=ride,
                    description=f"Pickup location assigned: {pickup_name}",
                    created_at=pickup_created_at - timedelta(minutes=10),
                )
            )

            events.append(
                RideEvent(
                    id_ride=ride,
                    description=f"Dropoff location assigned: {dropoff_name}",
                    created_at=pickup_created_at - timedelta(minutes=5),
                )
            )

            events.append(
                RideEvent(
                    id_ride=ride,
                    description=random.choice(
                        [
                            "Driver assigned",
                            "Driver arrived nearby",
                            "Rider notified",
                            "Route recalculated",
                            "Payment confirmed",
                        ]
                    ),
                    created_at=now - timedelta(
                        hours=random.randint(1, 24),
                        minutes=random.randint(0, 59),
                    ),
                )
            )

            events.append(
                RideEvent(
                    id_ride=ride,
                    description="Old ride event for performance test",
                    created_at=now - timedelta(days=random.randint(2, 15)),
                )
            )

        RideEvent.objects.bulk_create(events)