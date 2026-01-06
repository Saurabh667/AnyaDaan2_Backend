# from django.shortcuts import render
# from rest_framework import generics, status
# from rest_framework.response import Response
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import CustomUser
# from .serializers import SignupSerializer
# import json
# import random
# import os


# class RegisterView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = SignupSerializer


# @csrf_exempt
# def send_email_view(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             email = data.get("email")

#             if not email:
#                 return JsonResponse(
#                     {"error": "Email is required"},
#                     status=400
#                 )

#             otp = random.randint(100000, 999999)

#             message = f"""
# Hello,

# Welcome to AnyaDaan! 🌱
# We’re really happy to have you with us.
# Your account has been successfully created, and you’re now part of a community that believes in helping others and making a positive impact.

# What you can do with AnyaDaan:
# Explore and support meaningful causes
# Connect with people who want to make a difference
# Participate in donations and community initiatives
# If you ever need help or have questions, feel free to reply to this email—we’re always here to help.
# Thank you for joining us and being part of this journey.

#                             Warm regards,
#                             Team AnyaDaan
#                             Making kindness easier 🤍
#                         """

            
#             print(f"📧 Sending OTP {otp} to {email}")
#             from_email=os.getenv("DEFAULT_FROM_EMAIL") or os.getenv("EMAIL_HOST_USER")
#             send_mail(
#                 subject="Welcome to AnyaDaan – Thank You for Joining Us",
#                 message=message,
#                 from_email=from_email,
#                 recipient_list=[email],
#                 fail_silently=False,
#             )

#             return JsonResponse(
#                 {
#                     "message": "OTP sent successfully"
#                 },
#                 status=200
#             )

#         except Exception as e:
#             return JsonResponse(
#                 {"error": str(e)},
#                 status=500
#             )

#     return JsonResponse(
#         {"error": "Only POST method allowed"},
#         status=405
#     )

from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from django.core.mail import send_mail   # 🔴 CHANGED (removed SMTP usage)
from django.conf import settings
from .models import CustomUser
from .serializers import SignupSerializer
import json
import random
import os
import requests  # 🔴 CHANGED (added for SendGrid HTTP API)


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

            message = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>Welcome to AnyaDaan</title>
  </head>
  <body style="margin:0; padding:0; background-color:#f6f8fb; font-family: Arial, Helvetica, sans-serif;">

    <!-- Outer Wrapper -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f6f8fb; padding:30px 0;">
      <tr>
        <td align="center">

          <!-- Main Container -->
          <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:6px; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,0.08);">

            <!-- Header -->
            <tr>
              <td style="background-color:#22c55e; padding:20px; text-align:center;">
                <h1 style="color:#ffffff; margin:0; font-size:26px; letter-spacing:1px;">
                  AnyaDaan
                </h1>
              </td>
            </tr>

            <!-- Content -->
            <tr>
              <td style="padding:35px 40px; color:#111827;">
                <h2 style="margin-top:0; font-size:22px; color:#111827;">
                  Welcome to AnyaDaan 🌱
                </h2>

                <p style="font-size:15px; line-height:1.7; color:#374151;">
                  We’re really happy to have you with us.
                </p>

                <p style="font-size:15px; line-height:1.7; color:#374151;">
                  Your account has been successfully created, and you’re now part of a
                  community that believes in reducing food waste and helping people in need.
                </p>

                <p style="font-size:15px; line-height:1.7; color:#374151;">
                  Through AnyaDaan, you can connect with donors and receivers, contribute to
                  meaningful causes, and make a positive impact—one meal at a time.
                </p>

                <p style="margin-top:30px; font-size:15px; color:#374151;">
                  Warm regards,<br>
                  <strong>Team AnyaDaan</strong><br>
                  <span style="color:#22c55e;">Making kindness easier 🤍</span>
                </p>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td style="background-color:#f9fafb; padding:20px 40px; font-size:12px; color:#6b7280;">
                <p style="margin:0; line-height:1.6;">
                  You are receiving this email because you signed up on AnyaDaan.
                </p>
                <p style="margin:6px 0 0;">
                  © 2026 AnyaDaan • All rights reserved
                </p>
              </td>
            </tr>

          </table>

        </td>
      </tr>
    </table>

  </body>
</html>

"""

            print(f"📧 Sending OTP {otp} to {email}")

            SENDGRID_API_KEY = os.getenv("EMAIL_HOST_PASSWORD")   # 🔴 CHANGED
            FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")          # 🔴 CHANGED

            response = requests.post(                              # 🔴 CHANGED
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {SENDGRID_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [
                        {"to": [{"email": email}]}
                    ],
                    "from": {"email": FROM_EMAIL},
                    "subject": "Welcome to AnyaDaan – Thank You for Joining Us",
                    "content": [
                        {
                            "type": "text/html",
                            "value": message
                        }
                    ],
                },
                timeout=10,
            )

            if response.status_code not in (200, 202):             
                return JsonResponse(
                    {"error": response.text},
                    status=500
                )

            return JsonResponse(
                {"message": "OTP sent successfully"},
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
