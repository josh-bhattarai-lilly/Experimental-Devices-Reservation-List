import msal
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth import login as django_login
from django.http import HttpResponse
import requests
from django.contrib.auth import logout as django_logout
from .models import CustomUser  # Import the custom user model


def auth_callback(request):
    code = request.GET.get('code')  # Get the authorization code from the request
    if not code:
        return render(request, 'lilly_auth/error.html', {'error': 'Missing code parameter.'})

    msal_app = build_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=settings.MSAL_CONFIG['scopes'],
        redirect_uri=settings.MSAL_REDIRECT_URI
    )

    if 'access_token' in result:
        access_token = result['access_token']
        user_info = get_user_info(access_token)

        # Extract user info
        email = user_info.get('mail', '')
        username = email.split('@')[0]  # Use part of email as username (can be adjusted)
        first_name = user_info.get('givenName', '')
        last_name = user_info.get('surname', '')
        profile_picture_url = get_profile_picture_url(access_token)

        # Check if a user with the same email already exists
        user = CustomUser.objects.filter(email=email).first()

        if user:
            # If the user exists, just log them in
            django_login(request, user)
        else:
            # If the user does not exist, create a new one
            user = CustomUser.objects.create(username=username, email=email, first_name=first_name, last_name=last_name, profile_picture=profile_picture_url)
            django_login(request, user)

        # Save the access token in session to use for profile picture retrieval
        request.session['access_token'] = access_token

        return redirect('/')
    else:
        return render(request, 'lilly_auth/error.html', {'error': result.get('error', 'Unknown error')})


def build_msal_app():
    return msal.ConfidentialClientApplication(
        settings.MSAL_CLIENT_ID,
        authority=settings.MSAL_AUTHORITY,
        client_credential=settings.MSAL_CLIENT_SECRET,
    )


def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(settings.MSAL_USER_INFO_ENDPOINT, headers=headers)
    response.raise_for_status()  # Raise error for bad responses
    return response.json()


def get_profile_picture_url(access_token):
    graph_url = 'https://graph.microsoft.com/v1.0/me/photo/$value'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(graph_url, headers=headers)

    if response.status_code == 200:
        # Return the URL (or save the picture as a file if needed)
        return graph_url
    else:
        return '/static/images/pfp_red.png'


def login_view(request):
    msal_app = build_msal_app()
    auth_url = msal_app.get_authorization_request_url(settings.MSAL_CONFIG['scopes'])
    return redirect(auth_url)


def logout_view(request):
    django_logout(request)
    return redirect('/')


def profile_picture_view(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('/static/images/pfp_red.png')

    graph_url = 'https://graph.microsoft.com/v1.0/me/photo/$value'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(graph_url, headers=headers)

    if response.status_code == 200:
        return HttpResponse(response.content, content_type='image/jpeg')
    else:
        return redirect('/static/images/pfp_red.png')
