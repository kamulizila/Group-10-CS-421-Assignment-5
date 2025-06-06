from celery import shared_task 
from datetime import datetime, timezone, date  # ✅ Added date
from django.utils.timezone import now
from django.core.mail import send_mail
import requests
import ssl
import socket
import whois

from .models import Target, Status, History, Alert, SSLCheck, DomainCheck


# Meaningful HTTP status code messages
HTTP_STATUS_MEANINGS = {
    200: "OK",
    301: "Moved Permanently",
    302: "Found",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    408: "Request Timeout",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    # Add more as needed
}

def send_alert_email(message, target):
    send_mail(
        subject=f'[ALERT] Issue with {target.url}',
        message=message,
        from_email='umakomaward@gmail.com',
        recipient_list=['kamulizila97@gmail.com'],
    )

@shared_task
def check_targets_status():
    targets = Target.objects.all()
    for target in targets:
        try:
            start = datetime.now(timezone.utc)

            # Add User-Agent to reduce 403 errors
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(target.url, timeout=10, headers=headers)
            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            # Record the current status
            Status.objects.create(
                target_url=target,
                status_code=response.status_code,
                latency_ms=latency,
                checked_at=now(),
            )
            History.objects.create(
                target_url=target,
                status_code=response.status_code,
                latency_ms=latency,
                checked_at=now(),
            )

            # Get a human-readable description
            status_desc = HTTP_STATUS_MEANINGS.get(response.status_code, "Unknown Status")

            # Alert for statuses that indicate an issue
            if response.status_code >= 400:
                msg = f"Target {target.url} returned {response.status_code} ({status_desc})."
                Alert.objects.create(target_url=target, message=msg)
                send_alert_email(msg, target)

            # Alert if two consecutive failures (status code >= 400)
            recent_statuses = Status.objects.filter(target_url=target).order_by('-checked_at')[:2]
            if len(recent_statuses) == 2 and all(s.status_code >= 400 for s in recent_statuses):
                msg2 = f"Target {target.url} returned errors for two consecutive checks."
                Alert.objects.create(target_url=target, message=msg2)
                send_alert_email(msg2, target)

        except Exception as e:
            msg = f"Failed to check {target.url}: {str(e)}"
            Alert.objects.create(target_url=target, message=msg)
            send_alert_email(msg, target)
            

@shared_task
def check_ssl_and_domain_expiry():
    targets = Target.objects.all()
    for target in targets:
        try:
            # Extract hostname
            hostname = target.url.replace('https://', '').replace('http://', '').split('/')[0]

            # SSL Check
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    expire_str = cert['notAfter']
                    expires_at = datetime.strptime(expire_str, '%b %d %H:%M:%S %Y %Z')
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                    days_to_expiry = (expires_at - datetime.now(timezone.utc)).days

                    ssl_check, _ = SSLCheck.objects.get_or_create(target_url=target)
                    ssl_check.expires_at = expires_at
                    ssl_check.days_to_expiry = days_to_expiry
                    ssl_check.save()

                    if days_to_expiry <= 14:
                        msg = f"SSL certificate for {target.url} expires in {days_to_expiry} days."
                        Alert.objects.create(target_url=target, message=msg)
                        send_alert_email(msg, target)

            # Domain Check
            domain = hostname
            w = whois.whois(domain)
            domain_expiry = w.expiration_date

            # ✅ Handle various expiration_date types
            if isinstance(domain_expiry, list):
                domain_expiry = domain_expiry[0]

            if isinstance(domain_expiry, datetime):
                if domain_expiry.tzinfo is None:
                    domain_expiry = domain_expiry.replace(tzinfo=timezone.utc)
            elif isinstance(domain_expiry, date):
                domain_expiry = datetime.combine(domain_expiry, datetime.min.time(), tzinfo=timezone.utc)
            else:
                domain_expiry = None  # unknown format

            days_to_expiry = (domain_expiry - datetime.now(timezone.utc)).days if domain_expiry else None

            domain_check, _ = DomainCheck.objects.get_or_create(target_url=target)
            domain_check.expires_at = domain_expiry
            domain_check.days_to_expiry = days_to_expiry
            domain_check.save()

            if days_to_expiry is not None and days_to_expiry <= 14:
                msg = f"Domain registration for {target.url} expires in {days_to_expiry} days."
                Alert.objects.create(target_url=target, message=msg)
                send_alert_email(msg, target)

        except Exception as e:
            msg = f"Failed SSL/domain check for {target.url}: {str(e)}"
            Alert.objects.create(target_url=target, message=msg)
            send_alert_email(msg, target)

@shared_task
def ping_all_targets():
    """
    Aggregated task to perform both status check and SSL/domain expiry checks
    for all targets. This is useful for periodic scheduling via Celery Beat.
    """
    check_targets_status()
    check_ssl_and_domain_expiry()
