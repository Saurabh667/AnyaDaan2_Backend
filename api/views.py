from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
        except json.JSONDecodeError:
            return JsonResponse({ "error": "Invalid JSON" }, status=400)

        reply = "Thanks for your message! We’ll get back to you soon."

        return JsonResponse({ "reply": reply })

    return JsonResponse({ "error": "Only POST allowed" }, status=405)
