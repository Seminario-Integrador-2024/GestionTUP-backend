from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import PositiveIntegerField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for GestionTUP-backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    dni = PositiveIntegerField(
        _("DNI"),
        primary_key=True,
        null=False,
        blank=False,
        default=0,
    )
    full_name = CharField(
        _("Full Name of User"),
        blank=True,
        max_length=150,
        default="NonName",
    )
    first_name = None
    last_name = None
    email = EmailField(_("email address"), default="")
    username = None  # type: ignore[assignment]
    USERNAME_FIELD = "dni"
    REQUIRED_FIELDS = ["email"]
    objects: ClassVar[UserManager] = UserManager()

    def __str__(self) -> str:
        return self.email

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
