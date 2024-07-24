from django.contrib.auth.models import User
from django.db import models
from datetime import timedelta
from django.utils import timezone
class Partner(models.Model):
    """
    Model representing a partner in the system.
    """
    name = models.CharField(max_length=100)
    


class Store(models.Model):
    """
    Model representing a store associated with a partner.
    """
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    gst_number = models.CharField(max_length=15)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    is_active = models.BooleanField(default=True)


 #   managers = models.ManyToManyField(UserProfile, related_name='managed_stores')

class UserProfile(models.Model):
    """
    Model representing a user profile with a role (admin, manager, retailer).
    """

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('retailer', 'Retailer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='retailers')
    

class Item(models.Model):
    """
    Model representing an item available in the store.
    """

    ITEM_CHOICES = [
        ('tv', 'TV'),
        ('ac', 'AC'),
        ('mobile', 'Mobile'),
        ('laptop', 'Laptop'),
        ('washing_machine', 'Washing Machine')
    ]
    name = models.CharField(max_length=100,null=True, choices=ITEM_CHOICES)
    type = models.CharField(max_length=50)
    brand_warranty = models.IntegerField(default=12)  
    store = models.ForeignKey(Store, on_delete=models.CASCADE, default=1) 
    managerassignment = models.ForeignKey('ManagerAssignment', on_delete=models.SET_NULL, null=True, blank=True)
    retailerassignment = models.ForeignKey('RetailerAssignment', on_delete=models.SET_NULL, null=True, blank=True)
    manager=models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='items', default=1)
    item_purchase_date=models.DateField(default=timezone.now)
    esn_number = models.CharField(max_length=255, unique=True, default='1001')


class Customer(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    address=models.TextField()
    phone_number=models.CharField(max_length=10)

class Plan(models.Model):
    """
    Model representing a plan associated with an item.
    """

    PLAN_CHOICES = (
        ('extended_warranty', 'Extended Warranty'),
        ('screen_protection', 'Screen Protection'),
        ('adld', 'ADLD'),
        ('complete_care', 'Complete Care'),
        ('service', 'Service'),
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True, choices=PLAN_CHOICES)
    duration_in_months = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_plans', on_delete=models.SET_NULL, null=True)
    modified_by = models.ForeignKey(User, related_name='modified_plans', on_delete=models.SET_NULL, null=True)
    assigned_retailer = models.ForeignKey(UserProfile, related_name='assigned_plans', on_delete=models.CASCADE, null=True)
   


class PartnerItem(models.Model):
    """
    Model representing the association between a partner and an item.
    """

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
   


class PartnerPlan(models.Model):
    """
    Model representing the association between a partner and a plan.
    """

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)


class ManagerAssignment(models.Model):
    """
    Model representing the assignment of a manager to a store and a plan.
    """

    manager = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'manager'})
    #item = models.ForeignKey(Item, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    


class RetailerAssignment(models.Model):
    """
    Model representing the assignment of a retailer to a store and a plan.
    """

    retailer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'retailer'})
    #item = models.ForeignKey(Item, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    


class PlanSale(models.Model):
    """
    Model representing the sale of a plan associated with an item sale.
    """
    item=models.ForeignKey(Item, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    retailer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE)
    plan_purchase_date = models.DateField(default=timezone.now)
    plan_price= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    plan_start_date = models.DateField(null=True, blank=True)
    plan_end_date = models.DateField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.plan:
            plan_duration = self.plan.duration_in_months
            plan_name = self.plan.name
            item_purchase_date = self.item.item_purchase_date
            plan_purchase_date = self.plan_purchase_date

            if plan_name in ['extended_warranty', 'screen_protection']:
                
                brand_warranty = self.item.brand_warranty
                self.plan_start_date = item_purchase_date + timedelta(days=30 *brand_warranty)
                self.plan_end_date = self.plan_start_date + timedelta(days=30 *plan_duration)

            elif plan_name in ['adld', 'complete_care']:
                self.plan_start_date = plan_purchase_date
                self.plan_end_date = self.plan_start_date + timedelta(days=30*plan_duration)

            elif plan_name == 'service':
                self.plan_start_date = plan_purchase_date + timedelta(days=365)  # 12 months
                self.plan_end_date = self.plan_start_date + timedelta(days=30* plan_duration)

        super().save(*args, **kwargs)
   
# Create your models here