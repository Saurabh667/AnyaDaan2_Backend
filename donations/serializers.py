from rest_framework import serializers
from .models import donationData


class DonationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = donationData
        fields = [
            'id',
            'name',
            'email',
            'contributionType',
            'imageName',
            'description',
            'message',
            'created_at',
        ]
