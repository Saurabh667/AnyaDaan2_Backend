

from django.shortcuts import render
import razorpay
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .razorpay_client import razorpay_client
from .models import Payment
from razorpay.errors import SignatureVerificationError
from django.core.mail import send_mail
import os
import requests

client = razorpay_client


@api_view(['POST'])
def create_order(request):
    amount = request.data.get("amount")
    name = request.data.get("name")
    email = request.data.get("email")

    # ✅ CHANGE 2: Backend validation (VERY IMPORTANT)
    if not amount or not name or not email:
        return Response(
            {"error": "Amount, name and email are required"},
            status=400
        )

    order = client.order.create({
        "amount": int(amount) * 100,
        "currency": "INR",
        "payment_capture": 1
    })

    # ✅ CHANGE 3: Save payment safely
    Payment.objects.create(
        name=name,
        email=email,
        amount=amount,
        razorpay_order_id=order["id"],
        status="created"
    )

    return Response({
        "order_id": order["id"],
        "amount": order["amount"],
    })


# ================= VERIFY PAYMENT =================

@api_view(["POST"])
def verify_payment(request):
    data = request.data

    # ✅ CHANGE 4: Extract data safely
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    # ✅ CHANGE 5: Validate input before verification
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return Response(
            {"error": "Incomplete payment data"},
            status=400
        )

    try:
        # ✅ CHANGE 6: Verify Razorpay signature
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

        # ✅ CHANGE 7: Fetch payment safely
        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )

        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "success"
        payment.save()

        # ❌ BUG FIX: recipient_list must be EMAIL, not name
        # ✅ CHANGE 8: Fix email sending
        from_email=os.getenv("DEFAULT_FROM_EMAIL") or os.getenv("EMAIL_HOST_USER")
        SENDGRID_API_KEY = os.getenv("EMAIL_HOST_PASSWORD")   # unchanged
        FROM_EMAIL = from_email 
        response = requests.post(
    "https://api.sendgrid.com/v3/mail/send",
    headers={
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "personalizations": [
            {
                "to": [{"email": payment.email}]
            }
        ],
        "from": {
            "email": FROM_EMAIL
        },
        "subject": "Thank you for your contribution 🤍",
        "content": [
            {
                "type": "text/plain",
                "value": f"""
Hello {payment.name},

Thank you for your kind contribution on AnyaDaan.
Your generosity can make a real difference in someone’s life.

Warm regards,
Team AnyaDaan
Making kindness easier 🤍
                """
            }
        ],
    },
    timeout=10,
)

        if response.status_code not in (200, 202):
            raise Exception(response.text)
#         send_mail(
#             subject="Thank you for your contribution 🤍",
#             message=f"""
# Hello {payment.name},

# Thank you for your kind contribution on AnyaDaan.
# Your generosity can make a real difference in someone’s life.

# Warm regards,
# Team AnyaDaan
# Making kindness easier 🤍
#             """,
#             from_email=from_email,
#             recipient_list=[payment.email],  # ✅ FIXED
#             fail_silently=False,
#         )

#         print("Thank you email sent to:", payment.email)

        return Response({"status": "Payment verified successfully"})

    except Payment.DoesNotExist:
        
        return Response(
            {"error": "Payment record not found"},
            status=404
        )

    except SignatureVerificationError:
        Payment.objects.filter(
            razorpay_order_id=razorpay_order_id
        ).update(status="failed")

        return Response(
            {"status": "Payment verification failed"},
            status=400
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=500
        )
