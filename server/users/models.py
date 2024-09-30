from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
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
        help_text=_("Full name of the user."),
        blank=True,
        max_length=150,
        default="NonName",
    )
    first_name = None
    last_name = None
    username = None  # type: ignore[assignment]
    USERNAME_FIELD = "dni"
    REQUIRED_FIELDS = ["email"]
    objects = (
        UserManager()
    )  # this is the ORM manager. you can use it to query the database.
    # some examples are:
    # User.objects.all() -> returns all users
    # User.objects.get(dni=12345678) -> returns the user with dni 12345678
    # User.objects.filter(email="example@example.com") -> returns
    # all users with matched email

    def __str__(self) -> str:
        return self.full_name

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.dni})
