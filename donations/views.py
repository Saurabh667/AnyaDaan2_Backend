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
from rest_framework.decorators import api_view
from rest_framework.response import Response



class DonationCreateView(APIView):
    def post(self, request):
        serializer = DonationDataSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save()
            donation=serializer.save()
            receiversEmails=list(
            CustomUser.objects
            .filter(role='receiver')
            .values_list('email', flat=True)
            )
            if receiversEmails:
                subject = "New Contribution Available – AnyaDaan 🤍"

            message = f"""
A new contribution has been submitted on AnyaDaan.

Name: {donation.name}
Email: {donation.email}
Contribution Type: {donation.contributionType}

Description:{donation.description}

Message:{donation.message}


Request Time:{donation.created_at}
You can contact to recieve the donation.
                """
            send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=receiversEmails,
                    fail_silently=False,
                    )
            print(receiversEmails,'requests are send')


            contributor_email = donation.email  # adjust field name if different
            contributor_name = donation.name if hasattr(donation, 'name') else "Dear Contributor"
            send_mail(
                subject="Thank you for your contribution 🤍",
                message=f"""
Hello {contributor_name},
    Thank you for your kind contribution on AnyaDaan.
Your generosity can make a real difference in someone’s life.
We truly appreciate your support and willingness to help others.
Warm regards,
Team AnyaDaan
Making kindness easier 🤍
                                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contributor_email],
                fail_silently=False,
                )
            print('thanking mail send to ',contributor_email)


            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# receivers = CustomUser.objects.filter(role='receiver')
# print(receivers)

# receiversEmail=list(
#     CustomUser.objects
#     .filter(role='receiver')
#     .values_list('email', flat=True)
# )
# print(receiversEmail)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import donationData
from .serializers import DonationDataSerializer


@api_view(['GET'])

def donations_last_24_hours(request):
    # if request.user.role != "receiver":
    #     return Response(
    #         {"error": "Unauthorized"},
    #         status=403
    #     )
    last_24_hours = timezone.now() - timedelta(hours=24)

    donations = donationData.objects.filter(
        created_at__gte=last_24_hours
    ).order_by('-created_at')

    serializer = DonationDataSerializer(donations, many=True)
    return Response(serializer.data)