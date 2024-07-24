from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, PartnerViewSet, StoreViewSet, PlanViewSet,ItemViewSet,CustomAuthToken,  PlanSaleViewSet, PartnerItemViewSet, PartnerPlanViewSet, ManagerAssignmentViewSet, RetailerAssignmentViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Create a router and register our viewsets with it.

router = DefaultRouter()
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'items', ItemViewSet)
router.register(r'plans', PlanViewSet)
router.register(r'plansales', PlanSaleViewSet)
router.register(r'partneritems', PartnerItemViewSet)
router.register(r'partnerplans', PartnerPlanViewSet)
router.register(r'managerassignments', ManagerAssignmentViewSet)
router.register(r'retailerassignments', RetailerAssignmentViewSet)


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/custom-auth/', CustomAuthToken.as_view(), name='custom_auth_token'),  # Custom auth token view
    path('', include(router.urls)),
]
