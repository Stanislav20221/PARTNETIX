from datetime import timedelta

from django.utils import timezone


class LastActivityMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            now = timezone.now()

            if (
                not request.user.last_activity
                or now - request.user.last_activity > timedelta(seconds=30)
            ):
                request.user.last_activity = now
                request.user.save(update_fields=['last_activity'])

        return self.get_response(request)