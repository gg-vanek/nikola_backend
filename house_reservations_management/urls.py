from django.urls import path, include
from rest_framework import routers

from house_reservations_management.views.calendars import CalendarsViewSet
from house_reservations_management.views.house_reservations import HouseReservationsManagementViewSet
from house_reservations_management.views.houses import HouseListingViewSet

router = routers.SimpleRouter()
router.register(r'calendars', CalendarsViewSet)
router.register(r'', HouseReservationsManagementViewSet)
router.register(r'houses_list', HouseListingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
