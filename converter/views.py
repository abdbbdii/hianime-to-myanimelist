import os
import secrets
from typing import Literal
from datetime import datetime

import dotenv
import requests
from django.shortcuts import HttpResponse, redirect, render
from asgiref.sync import async_to_sync
from django.http import JsonResponse

from .HiAnime_to_MAL_API import get_hianime_list, populate_list, import_to_mal, check_cookie

dotenv.load_dotenv()

PUBLIC_URL = "https://hianime-to-mal.serveo.net"
MAL_TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
MAL_AUTHORIZATION_URL = "https://myanimelist.net/v1/oauth2/authorize"


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


# def start(request):
#     if request.POST.get("hi_cookie"):
#         request.session["hi_cookie"] = request.POST.get("hi_cookie")
#         headers = {"Authorization": f"Bearer {request.session['access_token']}"}

#         hi_list = get_hianime_list.get_list({"connect.sid": request.session["hi_cookie"]})
#         populated_list = populate_list.populate_list(hi_list, headers)
#         # return JsonResponse(populated_list)
#         import_to_mal.to_mal(populated_list["mal_list"], headers)
#         return HttpResponse("Done")

#     else:
#         return HttpResponse("No cookies provided", status=400)


async def start_async(request):
    try:
        headers = {"Authorization": f"Bearer {request.session['access_token']}"}
        print("Requesting list")
        hi_list = await get_hianime_list.get_list({"connect.sid": request.session["hi_cookie"]})
        print("Finding MAL IDs")
        populated_list = await populate_list.populate_list(hi_list, headers)
        print("Importing to MAL")
        await import_to_mal.to_mal(populated_list["mal_list"], headers)
        return {"status": "Transfer Successful!"}
    except Exception as e:
        return {"status": "Failed", "error": str(e)}

def start(request):
    if request.POST.get("hi_cookie") and check_cookie.is_valid({"connect.sid": request.POST.get("hi_cookie")}):
        request.session["hi_cookie"] = request.POST.get("hi_cookie")
        result = async_to_sync(start_async)(request)
        if result["status"] == "Transfer Successful!":
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=500)
    else:
        return JsonResponse({"status": "Invalid Cookie"}, status=400)


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
