import base64
import http.client
import json

from django.conf import settings
from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.gotoconnect.models import GoToConnectConfig, GoToConnectUser
from apps.profiles.models import UserProfile
from apps.tenants.models import Tenant
from apps.utils.tenants import get_tenant_from_request

from .serializers import GoToConnectConfigSerializer

GO_TO_CONNECT_REDIRECT_URL = f"{settings.BASE_URL}/api/v1/gotoconnect/auth"


class GoToConnectView(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    queryset = GoToConnectUser.objects.all()

    def get_queryset(self):
        tenant = get_tenant_from_request(self.request)
        return super().get_queryset().filter(tenant=tenant)

    # TODO: The client_id and client_secret should be hashed when passed to post request?
    @action(detail=False, methods=["post"])
    def add_integration(self, request: Request, pk=None):
        tenant: Tenant = get_tenant_from_request(request)
        request.data["tenant"] = tenant.id
        serializer: GoToConnectConfigSerializer = GoToConnectConfigSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        config = GoToConnectConfig.objects.filter(tenant=tenant).first()
        if config is None:
            serializer.save()
        else:
            serializer.update(instance=config, validated_data=serializer.validated_data)
        return Response({"message": {"Added integration to GoToConnect"}})

    @action(detail=False)
    def login(self, request: Request, pk=None):
        tenant: Tenant = get_tenant_from_request(request)
        client_id: str = GoToConnectConfig.objects.get(tenant=tenant).client_id
        if client_id is None:
            return Response(
                {"message": "Update GoToConnect Integration: Add client id"}
            )
        # Documentation: https://developer.goto.com/Authentication#tag/Authorize/paths/~1authorize/get
        login_request = f"oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={GO_TO_CONNECT_REDIRECT_URL}"
        return redirect(f"https://authentication.logmeininc.com/{login_request}")

    @action(detail=False)
    def auth(self, request: Request, pk=None):
        tenant: Tenant = get_tenant_from_request(request)
        client_id = GoToConnectConfig.objects.get(tenant=tenant).client_id
        client_secret = GoToConnectConfig.objects.get(tenant=tenant).client_secret
        auth_code = request.query_params.get("code")
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("ascii"))

        conn = http.client.HTTPSConnection("authentication.logmeininc.com")
        payload = f"grant_type=authorization_code&code={auth_code}&redirect_uri={GO_TO_CONNECT_REDIRECT_URL}&client_id={client_id}"

        headers = {
            "Authorization": auth_header,
            "content-type": "application/x-www-form-urlencoded",
        }

        conn.request("POST", "/oauth/token", payload, headers)

        res = conn.getresponse()
        data = res.read().decode("utf-8")
        json_data = json.loads(data)
        return Response(json_data)

    @action(detail=False, url_path="call")
    def initiate_call(self, request: Request, pk=None):

        call_to = request.query_params.get("call_to")
        user: UserProfile = request.user
        go_to_connect_user: GoToConnectUser = GoToConnectUser.objects.filter(
            user=user
        ).first()
        if go_to_connect_user is None:
            return Response({"message": "User has not logged into GoToConnect"})
        payload = {
            "dialString": call_to,
            "from": {"lineId": go_to_connect_user.line_id},
        }
        payload_str = json.dumps(payload)
        headers = {"content-type": "application/json"}

        conn = http.client.HTTPSConnection("api.jive.com")
        conn.request("POST", "/calls/v2/calls", payload_str, headers)
        res = conn.getresponse()
        data = res.read()
        return Response(json.loads(data))
