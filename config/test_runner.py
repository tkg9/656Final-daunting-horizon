from django.conf import settings
from django.test.runner import DiscoverRunner


class NoExternalServicesRunner(DiscoverRunner):
    """Blank the OpenRouter key for the whole run so no test can reach the real LLM,
    even when a developer has the key in their shell. Tests that need a key set a
    fake one with override_settings and mock the HTTP call."""

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        settings.OPENROUTER_API_KEY = ""
