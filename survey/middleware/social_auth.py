from django.shortcuts import redirect

from social_core.exceptions import AuthAlreadyAssociated
from social_django.middleware import SocialAuthExceptionMiddleware


class AuthAssociatedMiddleware(SocialAuthExceptionMiddleware):

    """Redirect users to desired-url when AuthAlreadyAssociated exception occurs."""
    def process_exception(self, request, exception):
        if isinstance(exception, AuthAlreadyAssociated):
            request.session.flush()
            return redirect(str.replace(getattr(request.backend,'redirect_uri'), 'complete', 'login'))