from rest_framework import serializers
from .models import Target, Status, History, Alert, SSLCheck, DomainCheck

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id', 'url', 'status','description', 'created_at']

# serializers.py
from rest_framework import serializers
from .models import Status

class StatusSerializer(serializers.ModelSerializer):
    target_url = serializers.CharField(source='target_url.url', read_only=True)

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

# from rest_framework import serializers
# from .models import DomainCheck

# class DomainCheckSerializer(serializers.ModelSerializer):
#     # target_url = serializers.CharField(source='target_url.url')  # this accesses Target.url
#     target_url = serializers.CharField(source='target.url', read_only=True)

#     class Meta:
#         model = DomainCheck
#         fields = ['id', 'target_url', 'expires_at', 'days_to_expiry', 'checked_at']

# serializers.py
from datetime import datetime
from django.utils.timezone import now

class DomainCheckSerializer(serializers.ModelSerializer):
    target_url = TargetSerializer(read_only=True)
    days_to_expiry = serializers.SerializerMethodField()

    class Meta:
        model = DomainCheck
        fields = ['id', 'target_url', 'expires_at', 'days_to_expiry', 'checked_at']

    def get_days_to_expiry(self, obj):
        if obj.expires_at:
            delta = obj.expires_at - now()
            return max(delta.days, 0)
        return None

