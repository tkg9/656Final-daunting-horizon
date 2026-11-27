"""Sign in with Google (OAuth 2.0 authorization-code flow).

Needs GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET. The Google client must list
https://<host>/auth/google/callback/ as an authorized redirect URI.
A verified Google email logs into the account with that email, creating it if needed.
"""
import json
import secrets
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def _redirect_uri(request):
    return request.build_absolute_uri(reverse("google-callback"))


def google_login(request):
    if not settings.GOOGLE_CLIENT_ID:
        raise Http404
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    next_url = request.GET.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
        request.session["google_oauth_next"] = next_url
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": _redirect_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return redirect(f"{AUTH_URL}?{urllib.parse.urlencode(params)}")


def _fetch_userinfo(request, code):
    body = urllib.parse.urlencode({
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": _redirect_uri(request),
        "grant_type": "authorization_code",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body), timeout=10) as response:
        access_token = json.load(response)["access_token"]
    userinfo = urllib.request.Request(USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
    with urllib.request.urlopen(userinfo, timeout=10) as response:
        return json.load(response)


def _fail(request, text):
    messages.error(request, text)
    return redirect("login")


def google_callback(request):
    expected_state = request.session.pop("google_oauth_state", None)
    next_url = request.session.pop("google_oauth_next", None) or settings.LOGIN_REDIRECT_URL
    if not expected_state or not secrets.compare_digest(request.GET.get("state", ""), expected_state):
        return _fail(request, "Google sign-in expired. Please try again.")
    code = request.GET.get("code")
    if not code:
        return _fail(request, "Google sign-in was cancelled.")
    try:
        info = _fetch_userinfo(request, code)
    except (urllib.error.URLError, KeyError, ValueError):
        return _fail(request, "Couldn't reach Google. Please try again.")
    email = (info.get("email") or "").strip().lower()
    if not email or info.get("email_verified") is not True:
        return _fail(request, "Your Google account has no verified email.")

    User = get_user_model()
    user = User.objects.filter(username__iexact=email).first()
    if user is None:
        user = User(username=email, email=email,
                    first_name=info.get("given_name", "")[:150], last_name=info.get("family_name", "")[:150])
        user.set_unusable_password()
        user.save()
    if not user.is_active:
        return _fail(request, "This account is disabled.")
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect(next_url)
