from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from .serializers import SignupSerializer
import json
import random
import os


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignupSerializer


@csrf_exempt
def send_email_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse(
                    {"error": "Email is required"},
                    status=400
                )

            otp = random.randint(100000, 999999)

            message = f"""
Hello,

Welcome to AnyaDaan! 🌱
We’re really happy to have you with us.
Your account has been successfully created, and you’re now part of a community that believes in helping others and making a positive impact.

What you can do with AnyaDaan:
Explore and support meaningful causes
Connect with people who want to make a difference
Participate in donations and community initiatives
If you ever need help or have questions, feel free to reply to this email—we’re always here to help.
Thank you for joining us and being part of this journey.

                            Warm regards,
                            Team AnyaDaan
                            Making kindness easier 🤍
                        """

            
            print(f"📧 Sending OTP {otp} to {email}")
            from_email=os.getenv("DEFAULT_FROM_EMAIL") or os.getenv("EMAIL_HOST_USER")
            send_mail(
                subject="Welcome to AnyaDaan – Thank You for Joining Us",
                message=message,
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse(
                {
                    "message": "OTP sent successfully"
                },
                status=200
            )

        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=500
            )

    return JsonResponse(
        {"error": "Only POST method allowed"},
        status=405
    )
