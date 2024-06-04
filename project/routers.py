from rest_framework import routers

from house_reservations_management.views.house_reservations import HouseReservationsViewSet
from house_reservations_management.views.calendars import CalendarsViewSet
from house_reservations_management.views.house_reservations_management import HouseReservationsManagementViewSet
from house_reservations_management.views.houses import HouseListingViewSet
from houses.views import HouseFeatureViewSet, HouseViewSet

houses_router = routers.SimpleRouter()
houses_router.register(r'features', HouseFeatureViewSet)
# Note: this CalendarsViewSet is located in HouseReservationsManagement package to avoid dependency problems
houses_router.register(r'', CalendarsViewSet)
houses_router.register(r'', HouseViewSet)
# Note: this HouseListingViewSet is located in HouseReservationsManagement package to avoid dependency problems
houses_router.register(r'', HouseListingViewSet)
# Note: this HouseReservationsViewSet is located in HouseReservations package to avoid dependency problems
houses_router.register(r'reservations', HouseReservationsViewSet)
# Note: this HouseReservationsViewSet is located in HouseReservationsManagement package to avoid dependency problems
houses_router.register(r'', HouseReservationsManagementViewSet)

