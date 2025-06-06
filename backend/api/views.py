from rest_framework import viewsets, permissions
import requests
from rest_framework.response import Response
from .models import Target, Status, History, Alert, SSLCheck, DomainCheck
from .serializers import (
    TargetSerializer, StatusSerializer, HistorySerializer,
    AlertSerializer, SSLCheckSerializer, DomainCheckSerializer
)

import requests
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Target
from .serializers import TargetSerializer

HTTP_STATUS_MEANINGS = {
    200: "OK",
    301: "Moved Permanently",
    302: "Found (Redirect)",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    # Add more if needed
}

class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36"
        }

        for item in data:
            url = item.get('url')
            try:
                response = requests.get(url, timeout=5, headers=headers)
                status_code = response.status_code
                status_description = HTTP_STATUS_MEANINGS.get(status_code, "Unknown Status")

                if 200 <= status_code < 300:
                    status = f"Up ({status_code} {status_description})"
                elif 300 <= status_code < 400:
                    status = f"Redirect ({status_code} {status_description})"
                elif 400 <= status_code < 500:
                    status = f"Client Error ({status_code} {status_description})"
                elif 500 <= status_code < 600:
                    status = f"Server Error ({status_code} {status_description})"
                else:
                    status = f"Other ({status_code} {status_description})"

            except requests.RequestException as e:
                status = f"Unavailable (Error: {str(e)})"

            item['status'] = status

        return Response(data)

    
    # permission_classes = [permissions.IsAuthenticated]

class StatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Status.objects.all().order_by('-checked_at')  # newest first
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


from rest_framework import viewsets
from rest_framework.response import Response
from .models import Status, Target
from .serializers import StatusSerializer

class LatestStatusViewSet(viewsets.ViewSet):
    def list(self, request):
        latest_statuses = []
        for target in Target.objects.all():
            latest = Status.objects.filter(target_url=target).order_by('-checked_at').first()
            if latest:
                latest_statuses.append(latest)
        serializer = StatusSerializer(latest_statuses, many=True)
        return Response(serializer.data)

# api/views.py
from django.utils.timezone import now, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import StatusLog
from .serializers import StatusLogSerializer

@api_view(['GET'])
def status_last_24h(request, target_id):
    since = now() - timedelta(hours=24)
    logs = StatusLog.objects.filter(target_id=target_id, timestamp__gte=since).order_by('timestamp')
    return Response(StatusLogSerializer(logs, many=True).data)
