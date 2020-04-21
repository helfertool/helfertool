from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.views.decorators.debug import sensitive_variables

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

import jmespath
import unicodedata


# the username is the mail address
def generate_username(email):
    return unicodedata.normalize('NFKC', email)[:150]


# whitelist logins via openid connect in django-axes as locking it the job if the identity provider
# (and we cannot do it properly with django-axes)
@sensitive_variables("credentials")
def axes_whitelist(request, credentials):
    if hasattr(request, "path") and request.path == reverse("oidc_authentication_callback"):
        return True

    return False


class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        verified = super(CustomOIDCAuthenticationBackend, self).verify_claims(claims)

        # we require the given_name and family_name
        if 'given_name' not in claims or 'family_name' not in claims:
            return False

        # abort login early when user is not allowed to login -> do not create account in database
        # this has the drawback that the "is_active" field of existing accounts is not updated
        # (anyway, the user would need to login for an attribute update)
        is_active = True
        if settings.OIDC_CUSTOM_CLAIM_LOGIN:
            is_active = self._check_claim_for_flag(claims, settings.OIDC_CUSTOM_CLAIM_LOGIN)

        return verified and is_active

    # called on first login when no user object exists
    def create_user(self, claims):
        user = super(CustomOIDCAuthenticationBackend, self).create_user(claims)

        # we also need to set the user attributes here
        return self.update_user(user, claims)

    # called on login when the user already exists, just update all attributes
    def update_user(self, user, claims):
        # name
        user.first_name = claims.get('given_name')
        user.last_name = claims.get('family_name')

        # check if login should be restricted (if not, login is allowed)
        if settings.OIDC_CUSTOM_CLAIM_LOGIN:
            user.is_active = self._check_claim_for_flag(claims, settings.OIDC_CUSTOM_CLAIM_LOGIN)

        # check if admin privilege should be assigned based on claims
        if settings.OIDC_CUSTOM_CLAIM_ADMIN:
            user.is_superuser = user.is_staff = self._check_claim_for_flag(claims, settings.OIDC_CUSTOM_CLAIM_ADMIN)

        user.save()
        return user

    def get_userinfo(self, access_token, id_token, payload):
        if settings.OIDC_OP_USER_ENDPOINT:
            return super(CustomOIDCAuthenticationBackend, self).get_userinfo(access_token, id_token, payload)
        else:
            # Assume payload of id_token contains all information
            return payload

    def _check_claim_for_flag(self, claims, conf):
        # get config and check if it is there
        compare = conf.get('compare', None)
        path = conf.get('path', None)
        value = conf.get('value', None)

        if compare is None or path is None or value is None:
            raise ImproperlyConfigured("Invalid OpenID Connect claim configuration (parameters missing)")

        # get claim value
        claim_value = jmespath.search(path, claims)

        if claim_value is None:
            return False

        # check claim
        if compare == 'direct':
            return claim_value == value
        elif compare == 'member':
            return type(claim_value) == list and value in claim_value
        else:
            raise ImproperlyConfigured("Invalid OpenID Connect claim configuration (invalid mode)")
