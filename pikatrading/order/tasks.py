from celery import shared_task
import requests
from django.core.mail import send_mail
from .models import Order
import time
import datetime
import json
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
from django.utils.timezone import now


@shared_task
def remove_unpaid_orders():
    threshold_time = now() - timedelta(minutes=2)
    Order.objects.filter(status="ordered", created_at__lt=threshold_time).delete()

