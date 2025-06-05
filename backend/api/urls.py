from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TargetViewSet, StatusViewSet, HistoryViewSet,
    AlertViewSet, SSLCheckViewSet, DomainCheckViewSet,
    LatestStatusViewSet
)

router = DefaultRouter()
router.register(r'targets', TargetViewSet)
router.register(r'status', StatusViewSet)
router.register(r'history', HistoryViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'ssl-checks', SSLCheckViewSet)
router.register(r'domain-checks', DomainCheckViewSet)

urlpatterns = [
    path('api/status/latest/', LatestStatusViewSet.as_view({'get': 'list'}), name='status-latest'),
    path('api/', include(router.urls)),
    
]
