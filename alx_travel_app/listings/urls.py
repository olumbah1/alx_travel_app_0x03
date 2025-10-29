from django.urls import path, include
from rest_framework import routers
from .views import (CustomUserViewSet, 
                    ListingViewSet, 
                    BookingViewSet,
                    ReviewViewSet,
                    InitializePaymentAPIView,
                    VerifyPaymentAPIView,
                    ChapaWebhookAPIView
                    )

router = routers.DefaultRouter()
router.register(r'user', CustomUserViewSet),
router.register(r'listing', ListingViewSet),
router.register(r'booking', BookingViewSet),
router.register(r'review', ReviewViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path("payments/initialize/", InitializePaymentAPIView.as_view(), name="initialize-payment"),
    path("payments/verify/<str:tx_ref>/", VerifyPaymentAPIView.as_view(), name="payments-verify"),
    path("payments/verify/", VerifyPaymentAPIView.as_view(), name="payments-verify-query"),
    path("payments/webhook/", ChapaWebhookAPIView.as_view(), name="payments-webhook"),
]