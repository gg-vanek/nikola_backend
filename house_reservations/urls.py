from django.urls import path, include
from rest_framework import routers
from house_reservations.views import HouseReservationsViewSet

router = routers.SimpleRouter()
router.register(r'', HouseReservationsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
