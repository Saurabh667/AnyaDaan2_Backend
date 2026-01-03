# from django.shortcuts import render

# # Create your views here.
# import razorpay
# from django.conf import settings
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .razorpay_client import razorpay_client
# from .models import Payment


# client = razorpay.Client(
#     auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
# )
# @api_view(['POST'])
# def create_order(request):
#     amount = request.data.get("amount")  # rupees
#     name = request.data.get("name")
#     email = request.data.get("email")

#     order = razorpay_client.order.create({
#         "amount": int(amount) * 100,  # paise
#         "currency": "INR",
#         "payment_capture": 1
#     })
#     Payment.objects.create(
#         name=name,
#         email=email,
#         amount=amount,
#         razorpay_order_id=order["id"],
#         status="created"
#     )

#     return Response({
#         "order_id": order["id"],
#         "amount": order["amount"],
#     })


# # to save the payment data 

# from razorpay.errors import SignatureVerificationError
# from django.core.mail import send_mail

# @api_view(["POST"])
# def verify_payment(request):
#     data = request.data

#     try:
#         client.utility.verify_payment_signature({
#             "razorpay_order_id": data["razorpay_order_id"],
#             "razorpay_payment_id": data["razorpay_payment_id"],
#             "razorpay_signature": data["razorpay_signature"],
#         })

#         payment = Payment.objects.get(
#             razorpay_order_id=data["razorpay_order_id"]
#         )

#         payment.razorpay_payment_id = data["razorpay_payment_id"]
#         payment.razorpay_signature = data["razorpay_signature"]
#         payment.status = "success"
#         payment.save()
#         send_mail(
#                 subject="Thank you for your contribution 🤍",
#                 message=f"""
# Hello {payment.name},
#     Thank you for your kind contribution on AnyaDaan.
# Your generosity can make a real difference in someone’s life.
# We truly appreciate your support and willingness to help others.
# Warm regards,
# Team AnyaDaan
# Making kindness easier 🤍
#                                 """,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[payment.name],
#                 fail_silently=False,
#                 )
#         print('thanking mail send to ',payment.email)

#         return Response({"status": "Payment verified"})

#     except SignatureVerificationError:
#         Payment.objects.filter(
#             razorpay_order_id=data["razorpay_order_id"]
#         ).update(status="failed")

#         return Response({"status": "Payment verification failed"}, status=400)

from django.shortcuts import render
import razorpay
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .razorpay_client import razorpay_client
from .models import Payment
from razorpay.errors import SignatureVerificationError
from django.core.mail import send_mail


# ❌ You already have razorpay_client, no need for duplicate client
# client = razorpay.Client(...)   ❌ REMOVED

# ✅ CHANGE 1: Use single client everywhere
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
        send_mail(
            subject="Thank you for your contribution 🤍",
            message=f"""
Hello {payment.name},

Thank you for your kind contribution on AnyaDaan.
Your generosity can make a real difference in someone’s life.

Warm regards,
Team AnyaDaan
Making kindness easier 🤍
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.email],  # ✅ FIXED
            fail_silently=False,
        )

        print("Thank you email sent to:", payment.email)

        return Response({"status": "Payment verified successfully"})

    except Payment.DoesNotExist:
        # ✅ CHANGE 9: Handle missing DB record
        return Response(
            {"error": "Payment record not found"},
            status=404
        )

    except SignatureVerificationError:
        # ✅ CHANGE 10: Mark payment as failed safely
        Payment.objects.filter(
            razorpay_order_id=razorpay_order_id
        ).update(status="failed")

        return Response(
            {"status": "Payment verification failed"},
            status=400
        )

    except Exception as e:
        # ✅ CHANGE 11: Prevent 500 crash
        return Response(
            {"error": str(e)},
            status=500
        )
