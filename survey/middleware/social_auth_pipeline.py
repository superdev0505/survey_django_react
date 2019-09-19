import logging

logger = logging.getLogger(__name__)

def existing_user_email(strategy, details, user=None, *args, **kwargs):

    """Update user details using data from provider."""
    if not user or getattr(user, 'email', None):
        logger.info('[AUTH PIPELINE] NO EMAIL {}'.format(user))
        return

    logger.info('[AUTH PIPELINE] add user details {}'.format(user))
    email = details.get('email')
    if email:
        setattr(user, 'email', email)
        logger.info('[AUTH PIPELINE] add new email {}'.format(email))
        return strategy.storage.user.changed(user)