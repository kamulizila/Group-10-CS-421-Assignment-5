from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TargetViewSet, StatusViewSet, HistoryViewSet,
    AlertViewSet, SSLCheckViewSet, DomainCheckViewSet,
    LatestStatusViewSet, status_last_24h
)

# Register all ViewSets
router = DefaultRouter()
router.register(r'targets', TargetViewSet)
router.register(r'status', StatusViewSet)
router.register(r'history', HistoryViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'ssl-checks', SSLCheckViewSet)
router.register(r'domain-checks', DomainCheckViewSet)

# Define all urlpatterns under the /api/ prefix
urlpatterns = [
    path('api/status/latest/', LatestStatusViewSet.as_view({'get': 'list'}), name='status-latest'),
    path('api/status_24h/<int:target_id>/', status_last_24h),  # ✅ This now lives under /api/
    path('api/', include(router.urls)),
]
