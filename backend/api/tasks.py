from celery import shared_task
from datetime import datetime, timezone
from django.utils.timezone import now
from django.core.mail import send_mail
import requests
import ssl
import socket
import whois

from .models import Target, Status, History, Alert, SSLCheck, DomainCheck


def send_alert_email(message, target):
    send_mail(
        subject=f'[ALERT] Issue with {target.url}',
        message=message,
        from_email='umakomaward@gmail.com',  # replace with your email
        recipient_list=['kamulizila97@gmail.com'],  # replace or make dynamic
    )


@shared_task
def check_targets_status():
    targets = Target.objects.all()
    for target in targets:
        try:
            start = datetime.now()
            response = requests.get(target.url, timeout=10)
            latency = (datetime.now() - start).total_seconds() * 1000  # ms

            # Save current status
            status = Status.objects.create(
                target=target,
                status_code=response.status_code,
                latency_ms=latency,
                checked_at=now(),
            )

            # Save to history
            History.objects.create(
                target=target,
                status_code=response.status_code,
                latency_ms=latency,
                checked_at=now(),
            )

            # Trigger alert if last two checks failed
            recent_statuses = Status.objects.filter(target=target).order_by('-checked_at')[:2]
            if len(recent_statuses) == 2 and all(s.status_code != 200 for s in recent_statuses):
                msg = f"Target {target.url} is down for two consecutive checks."
                Alert.objects.create(target=target, message=msg)
                send_alert_email(msg, target)

        except Exception as e:
            msg = f"Failed to check {target.url}: {str(e)}"
            Alert.objects.create(target=target, message=msg)
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

                    ssl_check, _ = SSLCheck.objects.get_or_create(target=target)
                    ssl_check.expires_at = expires_at
                    ssl_check.days_to_expiry = days_to_expiry
                    ssl_check.save()

                    if days_to_expiry <= 14:
                        msg = f"SSL certificate for {target.url} expires in {days_to_expiry} days."
                        Alert.objects.create(target=target, message=msg)
                        send_alert_email(msg, target)

            # Domain Check
            domain = hostname
            w = whois.whois(domain)
            domain_expiry = w.expiration_date
            if isinstance(domain_expiry, list):
                domain_expiry = domain_expiry[0]  # some WHOIS entries return a list

            days_to_expiry = (domain_expiry - datetime.now()).days if domain_expiry else None

            domain_check, _ = DomainCheck.objects.get_or_create(target=target)
            domain_check.expires_at = domain_expiry
            domain_check.days_to_expiry = days_to_expiry
            domain_check.save()

            if days_to_expiry is not None and days_to_expiry <= 14:
                msg = f"Domain registration for {target.url} expires in {days_to_expiry} days."
                Alert.objects.create(target=target, message=msg)
                send_alert_email(msg, target)

        except Exception as e:
            msg = f"Failed SSL/domain check for {target.url}: {str(e)}"
            Alert.objects.create(target=target, message=msg)
            send_alert_email(msg, target)
