import os
import secrets
from typing import Literal
from datetime import datetime
from datetime import timedelta

import requests
from django.utils import timezone
from django.http import JsonResponse
from dotenv import load_dotenv, find_dotenv
from django.shortcuts import HttpResponse, redirect, render

from .HiAnime_to_MAL_API import get_hianime_list, transfer_to_mal, check_cookie, delete_all, get_MAL

load_dotenv(find_dotenv()) if not os.getenv("VERCEL_ENV") else None

PUBLIC_URL = "https://hianime-to-mal.serveo.net"
MAL_TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
MAL_AUTHORIZATION_URL = "https://myanimelist.net/v1/oauth2/authorize"


def delete_all_anime(request):
    headers = {"Authorization": f"Bearer {request.session['access_token']}"}
    return JsonResponse({"status": delete_all.delete_all(headers)})


def get_json_list(request):
    headers = {"X-MAL-CLIENT-ID": os.getenv("MAL_CLIENT_ID")}
    return JsonResponse(get_MAL.get_MAL(headers, request.GET.get("username"), int(request.GET.get("offset_inc"))))


def is_expired(request) -> bool:
    if "access_token" in request.session:
        return (datetime.now() - datetime.fromisoformat(request.session["authorization_date"])).seconds > request.session["expires_in"]
    return True


def get_token(request, grant_type: Literal["authorization_code", "refresh_token"]) -> bool:
    token_data = {
        "client_id": os.getenv("MAL_CLIENT_ID"),
        "client_secret": os.getenv("MAL_CLIENT_SECRET"),
        "grant_type": grant_type,
    }
    if grant_type == "authorization_code":
        token_data["code"] = request.GET.get("code")
        token_data["code_verifier"] = request.session["code_challenge"]
    elif grant_type == "refresh_token":
        token_data["refresh_token"] = (request.session.get("refresh_token"),)

    response = requests.post(MAL_TOKEN_URL, data=token_data)
    if response.ok:
        request.session.update(response.json())
        request.session["authorization_date"] = datetime.now().isoformat()
        return True
    return False


def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]


def get_hi(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=400)
    try:
        hi_cookie = request.POST.get("hi_cookie")
        if not hi_cookie:
            return JsonResponse({"status": "Cookie not provided"}, status=400)
        if not check_cookie.is_valid({"connect.sid": hi_cookie}):
            return JsonResponse({"status": "Invalid cookie"}, status=400)
        request.session["hi_cookie"] = hi_cookie

        if request.session.get("hi_list") and request.session.get("hi_list_date"):
            last_reminder_time = datetime.fromisoformat(request.session.get("hi_list_date"))

            if timezone.is_naive(last_reminder_time):
                last_reminder_time = timezone.make_aware(last_reminder_time, timezone.get_default_timezone())

            if timezone.now() - last_reminder_time < timedelta(minutes=5):
                request.session["hi_list_date"] = timezone.now().isoformat()
                return JsonResponse({"message": "List retrieved successfully!", "count": len(request.session["hi_list"])})


        hi_list = get_hianime_list.get_list({"connect.sid": hi_cookie})
        response = {
            "message": "List retrieved successfully!",
            "count": len(hi_list),
        }
        request.session["hi_list"] = hi_list
        request.session["hi_list_date"] = timezone.now().isoformat()
        return JsonResponse(response, status=200)
    except Exception as e:
        return JsonResponse({"message": f"Failed to retrieve list: {str(e)}"}, status=500)


def send_to_mal(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=400)
    if not request.session.get("hi_list"):
        return JsonResponse({"message": "HiAnime list not found"}, status=400)

    try:
        hi_list = request.session.get("hi_list")
        from_index = int(request.POST.get("from"))
        to_index = int(request.POST.get("to"))

        anime_batch = hi_list[from_index:to_index]

        user_headers = {"Authorization": f"Bearer {request.session['access_token']}"}
        client_headers = {"X-MAL-CLIENT-ID": os.getenv("MAL_CLIENT_ID")}
        error_list = transfer_to_mal.transfer_to_mal(anime_batch, user_headers=user_headers, client_headers=client_headers)

        return JsonResponse({"message": "Transfer Successful!", "error_list": error_list})
    except Exception as e:
        return JsonResponse({"message": f"Failed to transfer to MAL: {str(e)}"}, status=500)


def index(request):
    if "access_token" in request.session and not is_expired(request):
        oauth_status = "Connected"
    elif "access_token" in request.session and is_expired(request) and get_token(request, "refresh_token"):
        oauth_status = "Connected"
    else:
        oauth_status = "Not connected"

    context = {
        "hi_cookie": request.session.get("hi_cookie") if request.session.get("hi_cookie") else "",
        "oauth_status": oauth_status,
    }
    return render(request, "index.html", context)


def oauth(request):
    code_challenge = request.session.get("code_challenge")

    if not code_challenge:
        request.session["code_challenge"] = get_new_code_verifier()
        params = {
            "response_type": "code",
            "client_id": os.getenv("MAL_CLIENT_ID"),
            "code_challenge": request.session["code_challenge"],
            "state": "RequestID42",
        }
        auth_url = requests.Request("GET", MAL_AUTHORIZATION_URL, params=params).prepare().url
        return redirect(auth_url)

    elif request.GET.get("code"):
        if get_token(request, "authorization_code"):
            return redirect("/")
        else:
            return HttpResponse(f"Error obtaining tokens (authorization_code)", status=400)

    elif request.session.get("access_token"):
        if is_expired(request):
            if get_token(request, "refresh_token"):
                return redirect("/")
            else:
                return HttpResponse("Error obtaining tokens (refresh_token)", status=400)
        else:
            return redirect("/")

    elif request.session.get("code_challenge") and not request.GET.get("code"):
        request.session.pop("code_challenge")
        return redirect("/oauth")
    else:
        return HttpResponse("Something went wrong.", status=400)
