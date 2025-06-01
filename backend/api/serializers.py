from rest_framework import serializers
from .models import Target, Status, History, Alert, SSLCheck, DomainCheck

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id', 'url', 'status','description', 'created_at']

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'target_url', 'status_code', 'latency_ms', 'checked_at']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'target_url', 'status_code', 'latency_ms', 'checked_at']

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'target_url', 'message', 'created_at', 'read']

class SSLCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSLCheck
        fields = ['id', 'target_url', 'expires_at', 'days_to_expiry', 'checked_at']

class DomainCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainCheck
        fields = ['id', 'target_url', 'expires_at', 'days_to_expiry', 'checked_at']
