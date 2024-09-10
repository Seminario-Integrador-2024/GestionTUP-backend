from dj_rest_auth.serializers import LoginSerializer as DRALoginSerializer
from dj_rest_auth.serializers import UserDetailsSerializer as DRADetailsSerializer
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.serializers import CharField

from server.users.models import User


class UserViewSetSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }
        lookup_field = "email"


class UserCreateSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "dni",
        )
        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }
        lookup_field = "email"


LEG_LENGTH = 5

DNI_MIN_LENGTH = 6
DNI_MAX_LENGTH = 9


class LoginSerializer(DRALoginSerializer):
    username = None
    email = None
    account = CharField(help_text="Email/Legajo/DNI")

    class Meta:
        model = User
        fields = ("password", "account")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def _validate_account(self, dni, leg, password):
        if dni:
            try:
                email = User.objects.get(dni__exact=dni).email
            except User.DoesNotExist:
                msg = _("tried 'DNI', but not found")
                raise exceptions.ValidationError(msg) from None
        else:
            try:
                email = User.objects.get(legajo__exact=leg).email
            except User.DoesNotExist:
                msg = _("tried 'Legajo', but not found")
                raise exceptions.ValidationError(msg) from None

        if email:
            return self.get_auth_user_using_allauth(None, email, password)

        return None

    def validate(self, attrs):
        account = attrs.get("account")
        password = attrs.get("password")
        user = None
        if "@" in account:  # login using allauth workflow
            user = self.get_auth_user(None, account, password)
            if "dj_rest_auth.registration" in settings.INSTALLED_APPS:
                self.validate_email_verification_status(user, email=account)
        elif account.isnumeric():
            leg_dni = len(str(account))
            if leg_dni == LEG_LENGTH:  # authenticate using, legajo
                # authenticate against django
                user = self._validate_account(None, account, password)
            elif DNI_MIN_LENGTH < leg_dni < DNI_MAX_LENGTH:
                user = self._validate_account(account, None, password)
        if not user:
            msg = _("Unable to log in with provided credentials.")
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?

        attrs["user"] = user
        return attrs


class UserDetailsSerializer(DRADetailsSerializer):
    class Meta:
        extra_fields = []
        model = User
        fields = "__all__"
        read_only_fields = ("email",)
