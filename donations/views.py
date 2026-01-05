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
import os
import requests


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
                "to": [{"email": e} for e in receiversEmails]
            }
        ],
        "from": {
            "email": FROM_EMAIL
        },
        "subject": subject,
        "content": [
            {
                "type": "text/plain",
                "value": message
            }
        ],
    },
    timeout=10,
)

            if response.status_code not in (200, 202):
                raise Exception(response.text)


            contributor_email = donation.email  # adjust field name if different
            contributor_name = donation.name if hasattr(donation, 'name') else "Dear Contributor"
            thanksMessage=f"""
Hello {contributor_name},
    Thank you for your kind contribution on AnyaDaan.
Your generosity can make a real difference in someone’s life.
We truly appreciate your support and willingness to help others.
Warm regards,
Team AnyaDaan
Making kindness easier 🤍
                                """
            SENDGRID_API_KEY = os.getenv("EMAIL_HOST_PASSWORD")
            from_email=os.getenv("DEFAULT_FROM_EMAIL") or os.getenv("EMAIL_HOST_USER")
            response = requests.post(
    "https://api.sendgrid.com/v3/mail/send",
    headers={
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "personalizations": [
            {"to": [{"email": contributor_email}]}
        ],
        "from": {"email": from_email},
        "subject": "Thank you for your contribution 🤍",
        "content": [
            {
                "type": "text/plain",
                "value": thanksMessage
            }
        ],
    },
    timeout=10,
)            
            if response.status_code not in (200, 202):
                raise Exception(response.text)
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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from .models import donationData

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def accept_donation(request, id):
    try:
        donation = donationData.objects.get(id=id)
        

        donation.status = "accepted"
        donation.accepted_by = request.user
        
        # receiversCompanyData = CustomUser.objects.filter(email=donation.accepted_by).values('company_name')
        # print(receiversCompanyData)
        receiversCompanyData = CustomUser.objects.filter(email=donation.accepted_by).values_list('company_name', flat=True).first()
        print(receiversCompanyData)
        message_to_donor = request.data.get("message_to_donor")

        donation.company_name = receiversCompanyData  # OR your company name
        donation.save()
        SENDGRID_API_KEY = os.getenv("EMAIL_HOST_PASSWORD")   
        from_email=os.getenv("DEFAULT_FROM_EMAIL") or os.getenv("EMAIL_HOST_USER")
        response = requests.post(
    "https://api.sendgrid.com/v3/mail/send",
    headers={
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "personalizations": [
            {
                "to": [{"email": donation.email}]
            }
        ],
        "from": {
            "email": from_email
        },
        "subject": "Your contribution has been accepted",
        "content": [
            {
                "type": "text/plain",
                "value": (
                    f"Hello {donation.name},\n\n"
                    f"Your contribution has been accepted by {donation.company_name}.\n"
                    f"Message from company:{message_to_donor}\n"
                    f"Company Email: {request.user.email}\n\n"
                    f"Thank you."
                )
            }
        ],
    },
    timeout=10,
)

        if response.status_code not in (200, 202):
            raise Exception(response.text)
        

        return Response({"message": "Accepted successfully"}, status=200)

    except donationData.DoesNotExist:
        return Response({"error": "Not found"}, status=404)





from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import donationData
from accounts.models import CustomUser

@api_view(['GET'])
def contribution_board(request):
    data = (
        donationData.objects
        .values('email', 'name')
        .annotate(total_donations=Count('id'))
        .order_by('-total_donations')
    )

    result = []

    for item in data:
        company = (
            CustomUser.objects
            .filter(email=item['email'])
            .values_list('company_name', flat=True)
            .first()
        )

        result.append({
            "name": item['name'],
            "company_name": company,
            "total_donations": item['total_donations']
        })

    return Response(result)
