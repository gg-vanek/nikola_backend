from django.urls import path, include
from rest_framework import routers
from houses.views import HouseFeatureViewSet, HouseViewSet

router = routers.SimpleRouter()
router.register(r'features', HouseFeatureViewSet)
router.register(r'', HouseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reservations/', include('house_reservations.urls')),
]
