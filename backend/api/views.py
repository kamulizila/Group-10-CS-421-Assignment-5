from rest_framework import viewsets, permissions
from .models import Target, Status, History, Alert, SSLCheck, DomainCheck
from .serializers import (
    TargetSerializer, StatusSerializer, HistorySerializer,
    AlertSerializer, SSLCheckSerializer, DomainCheckSerializer
)

class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    # permission_classes = [permissions.IsAuthenticated]

class StatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    # permission_classes = [permissions.IsAuthenticated]

class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    # permission_classes = [permissions.IsAuthenticated]

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    # permission_classes = [permissions.IsAuthenticated]

class SSLCheckViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SSLCheck.objects.all()
    serializer_class = SSLCheckSerializer
    # permission_classes = [permissions.IsAuthenticated]

class DomainCheckViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DomainCheck.objects.all()
    serializer_class = DomainCheckSerializer
    # permission_classes = [permissions.IsAuthenticated]
