
"""
views.py

This module contains viewsets for the API endpoints of the Django application, implementing role-based access control
for different user roles (admin, manager, retailer). Each viewset is responsible for handling CRUD operations for 
various models: Partner, Store, UserProfile, Item, Plan, ItemSale, and PlanSale. Custom permissions and queryset 
filters are applied based on the user's role.

Classes:
    CustomAuthToken
    PartnerViewSet
    StoreViewSet
    UserProfileViewSet
    ItemViewSet
    PlanViewSet
    ItemSaleViewSet
    PlanSaleViewSet
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from django.utils import timezone
from .models import Partner, Store,Customer ,UserProfile, Item, Plan, ManagerAssignment, RetailerAssignment, PlanSale, PartnerItem, PartnerPlan
from .serializers import PartnerSerializer,CustomerSerializer, StoreSerializer, UserProfileSerializer, ItemSerializer, PlanSerializer, ManagerAssignmentSerializer, RetailerAssignmentSerializer, PlanSaleSerializer, PartnerItemSerializer, PartnerPlanSerializer
from .permissions import IsAdmin, IsManager, IsRetailer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomAuthToken(TokenObtainPairView):
    """
    Custom authentication token view that returns the JWT token along with
    the user's ID, username, email, and role.
    """
    serializer_class = TokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data= serializer.validated_data # Validated data from the serializer
        token=data.get('access') # access token
        refresh_token=data.get('refresh')
        user=serializer.user
        return Response({
            'token': str(token),
            'refresh':str(refresh_token),
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'role': user.userprofile.role,
        })

class PartnerItemViewSet(viewsets.ModelViewSet):
    queryset = PartnerItem.objects.all()
    serializer_class = PartnerItemSerializer

class PartnerPlanViewSet(viewsets.ModelViewSet):
    queryset = PartnerPlan.objects.all()
    serializer_class = PartnerPlanSerializer

class ManagerAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ManagerAssignment.objects.all()
    serializer_class = ManagerAssignmentSerializer

class RetailerAssignmentViewSet(viewsets.ModelViewSet):
    queryset = RetailerAssignment.objects.all()
    serializer_class = RetailerAssignmentSerializer
    
class PartnerViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing partner instances.
    Only admin can access the partner model.
    """
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.request.user.userprofile.role == 'admin':
            return [permissions.AllowAny()]
        else:
            return [permissions.DjangoModelPermissions()]

class StoreViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing store instances.
    Only admin can create/edit the store instances. Other users can only view the instance.
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.userprofile.role in ['manager', 'retailer']:
            return Store.objects.filter(id=user.userprofile.store.id)
        elif user.userprofile.role == 'admin':
            return Store.objects.all()
        else:
            return Store.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.userprofile.role != 'admin':
            return Response({'error': 'You do not have permission to create a store.'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = request.user
        if user.userprofile.role != 'admin':
            return Response({'error': 'You do not have permission to update a store.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        current_user_profile = self.request.user.userprofile
        if current_user_profile.role == 'admin':
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'error': 'You do not have permission to delete a store.'}, status=status.HTTP_403_FORBIDDEN)

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user profile instances.
    Admin can view the profiles of all the users.
    Manager can just view his own profile and the profile of other retailers under him.
    Retailer can just view his own profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        current_user_profile = self.request.user.userprofile
        if current_user_profile.role == 'admin':
            return UserProfile.objects.all()
        elif current_user_profile.role == 'manager':
            return UserProfile.objects.filter(store=current_user_profile.store).exclude(role='admin')
        elif current_user_profile.role == 'retailer':
            return UserProfile.objects.filter(user=self.request.user)
        else:
            return UserProfile.objects.none()
    def create(self, serializer):
        current_user_profile = self.request.user.userprofile
        if current_user_profile.role == 'admin':
            serializer.save()
        elif current_user_profile.role == 'manager':
            if serializer.validated_data.get('role') == 'retailer' and serializer.validated_data.get('store') == current_user_profile.store:
                serializer.save()
            else:
                raise PermissionDenied("Managers can only create retailer profiles in their own store.")
        else:
            raise PermissionDenied("You do not have permission to perform this action.")
    def update(self, request, *args, **kwargs):
        current_user_profile = self.request.user.userprofile
        if current_user_profile.role == 'admin':
            return super().update(request, *args, **kwargs)
        elif current_user_profile.role == 'manager':
            instance = self.get_object()
            if instance.role == 'retailer':
                return super().update(request, *args, **kwargs)
            else:
                return Response({'error': 'Managers can only update retailer profiles.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'You do not have permission to update user profiles.'}, status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        current_user_profile = self.request.user.userprofile
        if current_user_profile.role == 'admin':
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'error': 'You do not have permission to delete user profiles.'}, status=status.HTTP_403_FORBIDDEN)

class ItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing item instances.
    Mangagers can just view/update the items listed under them
    Retailers can view the items whose plans they are selling.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.role == 'manager':
            assigned_stores = ManagerAssignment.objects.filter(manager=user.userprofile).values_list('store_id', flat=True)
            assigned_items = Item.objects.filter(partneritem__store__in=assigned_stores)
            return assigned_items
        elif user.userprofile.role == 'admin':
            return Item.objects.all()
        elif user.userprofile.role == 'retailer':
            assigned_plans = Plan.objects.filter(assigned_retailer=user.userprofile)
            item_ids = assigned_plans.values_list('item_id', flat=True)
            return Item.objects.filter(id__in=item_ids)

        else:
            return Item.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.userprofile.role != 'admin':
            raise PermissionDenied('You do not have permission to create an item.')
        return super().create(request, *args, **kwargs)
    def update(self, request, *args, **kwargs):
        if request.user.userprofile.role != 'admin':
            raise PermissionDenied('You do not have permission to update items.')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.userprofile.role != 'admin':
            raise PermissionDenied('You do not have permission to delete items.')
        return super().destroy(request, *args, **kwargs)


class PlanViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing plan instances.
    Managers can create/update the plans whose items that are assigned.
    Retailer can just view the plan assigned to him.
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        elif self.request.user.userprofile.role == 'admin':
            return [IsAdmin()]
        elif self.request.user.userprofile.role == 'manager':
            return [IsManager()]
        elif self.request.user.userprofile.role == 'retailer':
            return [IsRetailer()]
        return [permissions.DjangoModelPermissions()]

    def get_queryset(self):
        user = self.request.user
        print("role : ", user.userprofile.role)
        if user.userprofile.role == 'admin':
            return Plan.objects.all()
        elif user.userprofile.role == 'manager':
            manager_assignments = ManagerAssignment.objects.filter(manager=user.userprofile)
            print("manager querset : ", manager_assignments.count())
            store_ids = manager_assignments.values_list('store_id', flat=True)
            print("stores_id : ", store_ids.count())
            print("result : ", Plan.objects.filter(item__store__id__in=store_ids))
            return Plan.objects.filter(item__managerassignment__store__id__in=store_ids)
        elif user.userprofile.role == 'retailer':
            retailer_assignments = RetailerAssignment.objects.filter(retailer=user.userprofile)
            store_ids = retailer_assignments.values_list('store_id', flat=True)
            return Plan.objects.filter(item__store__id__in=store_ids)
        return Plan.objects.none()
    def create(self, request, *args, **kwargs):
        if request.user.userprofile.role not in ['manager', 'admin']:
            raise PermissionDenied('You do not have permission to create a plan.')
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.userprofile.role not in ['manager', 'admin']:
            raise PermissionDenied('You do not have permission to update a plan.')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.userprofile.role != 'admin':
            raise PermissionDenied('You do not have permission to delete a plan.')
        return super().destroy(request, *args, **kwargs)
    


class PlanSaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing PlanSale instances.
    Retailers have access to update/create the plansale instance as retailers are the ones who are selling the plans
    Manager and admin can also access this instance.
    """

    queryset = PlanSale.objects.all()
    serializer_class = PlanSaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        elif self.request.user.userprofile.role == 'retailer':
            return [permissions.IsAuthenticated()]
        return [permissions.DjangoModelPermissions()]

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.role == 'admin':
            return PlanSale.objects.all()
        elif user.userprofile.role == 'manager':
            manager_assignments = ManagerAssignment.objects.filter(manager=user.userprofile)
            store_ids = manager_assignments.values_list('store_id', flat=True)
            return PlanSale.objects.filter(plan__item__managerassignment__store__id__in=store_ids)
        elif user.userprofile.role == 'retailer':
            retailer_assignments = RetailerAssignment.objects.filter(retailer=user.userprofile)
            store_ids = retailer_assignments.values_list('store_id', flat=True)
            return PlanSale.objects.filter(plan__item__retailerassignment__store__id__in=store_ids)
        else:
            return PlanSale.objects.none()
        
    def perform_create(self, serializer):
        # Check if item is being posted and handle accordingly
        
        serializer.save()


 
    def update(self, request, *args, **kwargs):
        retailer = request.user.userprofile
        plan_id = request.data.get('plan')
        #item_id = request.data.get('item')
        esn_number = request.data.get('esn_number')


        try:
            plan = Plan.objects.get(id=plan_id)
            item = Item.objects.get(esn_number=esn_number)
        except (Plan.DoesNotExist, Item.DoesNotExist):
            return Response({'error': 'Plan or Item not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if not RetailerAssignment.objects.filter(retailer=retailer, plan=plan, store=item.store).exists():
            return Response({'error': 'Item is not assigned to you.'}, status=status.HTTP_403_FORBIDDEN)

        if item != plan.item:
            return Response({'error': 'Item associated with the plan must be the same.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)
       

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        retailer = request.user.userprofile
        plan_sale = self.get_object()

        if not RetailerAssignment.objects.filter(retailer=retailer, plan=plan_sale.plan, store=plan_sale.item.store).exists():
            return Response({'error': 'You do not have permission to delete this plan sale.'}, status=status.HTTP_403_FORBIDDEN)


        return super().destroy(request, *args, **kwargs)

