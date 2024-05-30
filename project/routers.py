from rest_framework import routers

from house_reservations.views import HouseReservationsViewSet
from house_reservations_management.views.calendars import CalendarsViewSet
from house_reservations_management.views.house_reservations import HouseReservationsManagementViewSet
from house_reservations_management.views.houses import HouseListingViewSet
from houses.views import HouseFeatureViewSet, HouseViewSet

houses_router = routers.SimpleRouter()
houses_router.register(r'houses/features', HouseFeatureViewSet)
houses_router.register(r'houses', HouseViewSet)
# Note: this HouseListingViewSet is located in HouseReservationsManagement package to avoid dependency problems
houses_router.register(r'houses', HouseListingViewSet)

house_reservations_router = routers.SimpleRouter()
house_reservations_router.register(r'house_reservations', HouseReservationsViewSet)

house_reservations_management_router = routers.SimpleRouter()
house_reservations_management_router.register(r'house_reservation_management/calendars', CalendarsViewSet)
house_reservations_management_router.register(r'house_reservation_management', HouseReservationsManagementViewSet)
