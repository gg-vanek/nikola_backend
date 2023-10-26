from houses.views import HouseFeatureViewSet, HouseViewSet
from django.urls import path, include
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'features', HouseFeatureViewSet)
router.register(r'', HouseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
