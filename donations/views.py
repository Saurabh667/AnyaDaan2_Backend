from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DonationDataSerializer
from accounts.models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import json
from django.conf import settings


class DonationCreateView(APIView):
    def post(self, request):
        serializer = DonationDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

receivers = CustomUser.objects.filter(role='receiver')
print(receivers)

receiversEmail=list(
    CustomUser.objects
    .filter(role='receiver')
    .values_list('email', flat=True)
)
print(receiversEmail)
for i in range(0,len(receiversEmail)):
        selectedMail=receiversEmail[i]
        
        @csrf_exempt
        def send_email_view(request):
            if request.method == "POST":
                try:
                    data = json.loads(request.body)
                    email = selectedMail
                    # companyName=data.name

                    if not email:
                        return JsonResponse(
                            {"error": "Email is required"},
                            status=400
                        )

                    # otp = random.randint(100000, 999999)

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

                    # Debug log
                    

                    send_mail(
                        subject="A Donation request is being posted.",
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )

                    return JsonResponse(
                        {
                            "message": "OTP sent successfully",
                            "otp": receiversEmail  
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

