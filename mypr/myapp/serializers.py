from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Partner, Store, Item, Plan, PartnerItem, PartnerPlan, ManagerAssignment, RetailerAssignment, PlanSale, Customer

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class PartnerItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerItem
        fields = '__all__'

class PartnerPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerPlan
        fields = '__all__'

class ManagerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerAssignment
        fields = '__all__'

class RetailerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetailerAssignment
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'address', 'phone_number']


class PlanSaleSerializer(serializers.ModelSerializer):
    
    customer = CustomerSerializer(required=False)
    esn_number = serializers.CharField(write_only=True)  
    class Meta:
        model = PlanSale
        fields = '__all__'
        read_only_fields = ['retailer', 'plan_start_date', 'plan_end_date']

    def validate(self, data):
        esn_number = data.get('esn_number')
        if esn_number:
            try:
                item = Item.objects.get(esn_number=esn_number)
            except Item.DoesNotExist:
                raise serializers.ValidationError({"esn_number": "Item with this ESN number does not exist."})

            if PlanSale.objects.filter(item=item).exists():
                raise serializers.ValidationError({"esn_number": "ESN number already sold."})
            
            data['item'] = item
        
        return data

    def create(self, validated_data):
        # Extract the customer data if provided
        customer_data = validated_data.pop('customer', None)
        esn_number = validated_data.pop('esn_number', None)
        item = validated_data.pop('item', None)

        # Get the retailer from the request context
        retailer = self.context['request'].user.userprofile
        
        # Handle customer creation or retrieval
        if customer_data:
            customer, created = Customer.objects.get_or_create(**customer_data)
        else:
            customer = None
        
        # Create PlanSale instance
        plansale = PlanSale.objects.create(customer=customer, retailer=retailer,item=item, **validated_data)
        return plansale