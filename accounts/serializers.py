from rest_framework import serializers
from .models import CustomUser

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    companyName = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'companyName',
            'role',
            'first_name',
            'last_name',
            'phone',
            'email',
            'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        company_name = validated_data.pop('companyName')

        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=password,
            company_name=company_name,
            role=validated_data.get('role'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone=validated_data.get('phone'),
        )

        return user
