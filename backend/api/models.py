from django.db import models

class Target(models.Model):
    url = models.URLField(unique=True)
    status = models.CharField(max_length=10, default='N/A')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url

class Status(models.Model):
    target_url = models.ForeignKey(Target, related_name='statuses', on_delete=models.CASCADE)
    status_code = models.IntegerField()
    latency_ms = models.FloatField()
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.target_url.url} - {self.status_code} at {self.checked_at}"  # Changed to target_url.url

class History(models.Model):
    target_url = models.ForeignKey(Target, related_name='histories', on_delete=models.CASCADE)
    status_code = models.IntegerField()
    latency_ms = models.FloatField()
    checked_at = models.DateTimeField()

    def __str__(self):
        return f"History: {self.target_url.url} - {self.status_code} at {self.checked_at}"  # Changed

class Alert(models.Model):
    target_url = models.ForeignKey(Target, related_name='alerts', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert for {self.target_url.url} at {self.created_at}"  # Changed

class SSLCheck(models.Model):
    target_url = models.OneToOneField(Target, related_name='ssl_check', on_delete=models.CASCADE)
    expires_at = models.DateTimeField(null=True, blank=True)
    days_to_expiry = models.IntegerField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SSL for {self.target_url.url} expires {self.expires_at}"  # Changed

class DomainCheck(models.Model):
    target_url = models.OneToOneField(Target, related_name='domain_check', on_delete=models.CASCADE)
    expires_at = models.DateTimeField(null=True, blank=True)
    days_to_expiry = models.IntegerField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Domain for {self.target_url.url} expires {self.expires_at}"

# api/models.py
class StatusLog(models.Model):
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    status_code = models.IntegerField()
    response_time = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
