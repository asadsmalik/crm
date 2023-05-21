from django.contrib.auth.models import Group
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from apps.roles.models import (DEFAULT_ADMIN_ROLE_NAME,
                               DEFAULT_MANAGER_ROLE_NAME,
                               DEFAULT_SALES_ROLE_NAME, Role)
from apps.roles.role_permissions import (get_admin_permissions,
                                         get_manager_permissions,
                                         get_sales_permissions)
from apps.tenants.models import Tenant
from apps.tenants.serializers import TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    queryset = Tenant.objects.all()
    authentication_classes = (TokenAuthentication,)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # Add a default Admin Role which has access to everything for the tenant
    def create_admin_role(self, tenant: Tenant):
        admin_group, _ = Group.objects.get_or_create(name=f"{tenant.id}_{DEFAULT_ADMIN_ROLE_NAME}")
        admin_permissions = get_admin_permissions()
        admin_group.permissions.set(admin_permissions)
        admin_role: Role = Role(name=f"{tenant.id}_{DEFAULT_ADMIN_ROLE_NAME}", group=admin_group, tenant=tenant)
        admin_group.save()
        admin_role.save()
    
    def create_manager_role(self, tenant: Tenant):
        manager_group, _ = Group.objects.get_or_create(name=f"{tenant.id}_{DEFAULT_MANAGER_ROLE_NAME}")
        manager_permissions = get_manager_permissions()
        manager_group.permissions.set(manager_permissions)
        manager_role: Role = Role(name=f"{tenant.id}_{DEFAULT_MANAGER_ROLE_NAME}", group=manager_group, tenant=tenant)
        manager_group.save()
        manager_role.save()
    
    def create_sales_role(self, tenant: Tenant):
        sales_group, _ = Group.objects.get_or_create(name=f"{tenant.id}_{DEFAULT_SALES_ROLE_NAME}")
        sales_permissions = get_sales_permissions()
        sales_group.permissions.set(sales_permissions)
        sales_role: Role = Role(name=f"{tenant.id}_{DEFAULT_SALES_ROLE_NAME}", group=sales_group, tenant=tenant)
        sales_group.save()
        sales_role.save()

    def create(self, request, *args, **kwargs):
        # Only staff is allowed to create new tenants
        #if not request.user.is_staff:
        #    return Response({status.HTTP_404_NOT_FOUND})
    
        # Create the Tenant
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        tenant: Tenant = Tenant.objects.get(name=serializer.validated_data["name"])
        self.create_admin_role(tenant=tenant)
        self.create_manager_role(tenant=tenant)
        self.create_sales_role(tenant=tenant)

        # Return success response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
