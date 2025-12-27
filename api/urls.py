from django.urls import path
from accounts import views as UserViews
from accounts import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from donations import views as donationViews


urlpatterns = [
    path('signup/',UserViews.RegisterView.as_view()),
    path('sendEmail/', views.send_email_view), 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('donationData/',donationViews.DonationCreateView.as_view()),
    path("donations/recent/", donationViews.donations_last_24_hours),
    path("donations/<int:id>/accept/", donationViews.accept_donation),
    path("contributions/board",donationViews.contribution_board),
    



]
