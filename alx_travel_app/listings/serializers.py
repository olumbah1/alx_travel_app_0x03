from rest_framework import serializers
from .models import CustomUser, Listing, Booking, Review, Payment
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError, PermissionDenied

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ["user_id", "email", "first_name", "last_name", "password"]
        
    def create(self, validated_data):
        password = validated_data.pop("password")
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise DRFValidationError({"password": list(e.messages)})
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ListingSerializer(serializers.ModelSerializer):
    host = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    host = serializers.ReadOnlyField(source='host.user_id')
    class Meta:
        model = Listing
        fields = ["listing_id", "title", "description",
                  "host", "street", "city", 
                  "state", "postal_code", "country",
                  "created_at", "is_active"]
    
    
class BookingSerializer(serializers.ModelSerializer):
    listing_id = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    user = serializers.ReadOnlyField(source='user.user_id')
    class Meta:
        model = Booking
        fields = ["booking_id", "listing_id", "user_id",
                  "start_date", "end_date", "status", "user",
                  "created_at"]
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this booking.")
        serializer.save()

class ReviewSerializer(serializers.ModelSerializer):
    listing_id = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    user = serializers.ReadOnlyField(source='user.user_id')
    class Meta:
        model = Review
        fields = ["review_id", "listing_id", "user", "user_id", 
                  "comment", "rating", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "user", "booking_reference", "transaction_id",
            "amount", "currency", "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "transaction_id", "status", "created_at", "updated_at"]
    


