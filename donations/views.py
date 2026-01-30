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
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>New Contribution – AnyaDaan</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial,Helvetica,sans-serif;">

  <!-- Outer Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:30px 0;">
    <tr>
      <td align="center">

        <!-- Main Card -->
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#22c55e,#16a34a);padding:24px;text-align:center;color:#ffffff;">
              <h1 style="margin:0;font-size:26px;">🌱 AnyaDaan</h1>
              <p style="margin:6px 0 0;font-size:14px;opacity:0.95;">
                Connecting surplus food with those in need
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:28px;color:#111827;">
              <h2 style="margin-top:0;font-size:20px;color:#16a34a;">
                New Contribution Available 🤍
              </h2>

              <p style="font-size:15px;line-height:1.6;color:#374151;">
                A new contribution has just been submitted on <strong>AnyaDaan</strong>.
                Please find the details below:
              </p>

              <!-- Info Box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;">
                <tr>
                  <td style="padding:8px 0;"><strong>👤 Name:</strong> {donation.name}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0;"><strong>📧 Email:</strong> {donation.email}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0;"><strong>🍽 Contribution Type:</strong> {donation.contributionType}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0;"><strong>🕒 Request Time:</strong> {donation.created_at}</td>
                </tr>
                <tr>
                  <td style="padding:8px 0;"><strong>Link:</strong> https://anya-daan2-frontend.vercel.app/recentDonations</td>
                </tr>
              </table>

              <!-- Description -->
              <p style="margin-top:18px;font-size:15px;">
                  
                <strong>📝 Description:</strong><br>
                {donation.description}
              </p>

              <!-- Message -->
              <p style="font-size:15px;">
                <strong>💬 Message from Contributor:</strong><br>
                {donation.message}
              </p>

              <!-- CTA -->
              <div style="margin-top:24px;padding:16px;background:#ecfdf5;border-left:4px solid #22c55e;border-radius:6px;">
                <p style="margin:0;font-size:14px;color:#065f46;">
                  You may contact the contributor directly to receive and coordinate this donation.
                </p>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9fafb;padding:18px;text-align:center;font-size:12px;color:#6b7280;">
              © 2026 AnyaDaan • Making kindness easier 🤍  
              <br>
              Please do not reply to this automated email.
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>

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
                "type": "text/html",
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
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Thank You – AnyaDaan</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial,Helvetica,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:30px 0;">
    <tr>
      <td align="center">

        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:10px;overflow:hidden;
                      box-shadow:0 6px 18px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#22c55e,#16a34a);
                       padding:26px;text-align:center;color:#ffffff;">
              <h1 style="margin:0;font-size:26px;">🤍 Thank You!</h1>
              <p style="margin-top:6px;font-size:14px;opacity:0.95;">
                Your generosity makes a difference
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:28px;color:#111827;">
              <p style="font-size:16px;margin-top:0;">
                Hello <strong>{contributor_name}</strong>,
              </p>

              <p style="font-size:15px;line-height:1.7;color:#374151;">
                Thank you for your kind contribution on <strong>AnyaDaan</strong>.
                Your generosity can make a real difference in someone’s life.
              </p>

              <p style="font-size:15px;line-height:1.7;color:#374151;">
                We truly appreciate your support and willingness to help others.
                Because of people like you, surplus food reaches those who need it most.
              </p>

              <div style="margin-top:22px;padding:16px;
                          background:#ecfdf5;border-left:4px solid #22c55e;
                          border-radius:6px;">
                <p style="margin:0;font-size:14px;color:#065f46;">
                  🌱 Together, we are building a more responsible and caring community.
                </p>
              </div>

              <p style="margin-top:24px;font-size:15px;">
                Warm regards,<br>
                <strong>Team AnyaDaan</strong><br>
                <span style="color:#16a34a;">Making kindness easier 🤍</span>
                
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9fafb;padding:16px;text-align:center;
                       font-size:12px;color:#6b7280;">
              © 2026 AnyaDaan • Thank you for being a changemaker
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>
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
                "type": "text/html",
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
                "type": "text/html",
                "value":f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Contribution Accepted</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:Arial,Helvetica,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
       style="background:#ffffff;border-radius:10px;
              box-shadow:0 6px 18px rgba(0,0,0,0.08);overflow:hidden;">

<!-- Header -->
<tr>
<td style="background:linear-gradient(135deg,#22c55e,#16a34a);
           padding:24px;text-align:center;color:#ffffff;">
<h2 style="margin:0;">✅ Contribution Accepted</h2>
<p style="margin-top:6px;font-size:14px;">
Thank you for your kindness 🤍
</p>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:26px;color:#111827;">

<p style="font-size:16px;">
Hello <strong>{donation.name}</strong>,
</p>

<p style="font-size:15px;line-height:1.7;color:#374151;">
Your contribution has been successfully accepted by
<strong>{donation.company_name}</strong>.
</p>

<div style="margin:20px 0;padding:16px;
            background:#ecfdf5;border-left:4px solid #22c55e;
            border-radius:6px;">
<p style="margin:0;font-size:14px;color:#065f46;">
<strong>Message from the organization:</strong><br><br>
{message_to_donor}
</p>
</div>

<p style="font-size:15px;line-height:1.7;color:#374151;">
If you wish to get in touch, you can contact them at:
</p>

<p style="font-size:14px;">
📧 <strong>{request.user.email}</strong>
</p>

<p style="margin-top:24px;font-size:15px;">
Thank you once again for making a difference.
</p>

<p style="margin-top:20px;">
Warm regards,<br>
<strong>Team AnyaDaan</strong><br>
<span style="color:#16a34a;">Making kindness easier 🤍</span>
</p>

</td>
</tr>

<!-- Footer -->
<tr>
<td style="background:#f9fafb;padding:14px;text-align:center;
           font-size:12px;color:#6b7280;">
© 2026 AnyaDaan • Together against food waste
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""
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
