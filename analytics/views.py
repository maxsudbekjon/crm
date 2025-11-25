from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count
from .models import Click
from apps.models import Lead


# --- 1) Source aniqlash ---
def detect_source(request):
    ua = request.META.get("HTTP_USER_AGENT", "").lower()

    if "instagram" in ua:
        return "instagram"
    elif "telegram" in ua or "t.me" in ua:
        return "telegram"
    elif "facebook" in ua or "fb" in ua:
        return "facebook"
    elif "whatsapp" in ua:
        return "whatsapp"
    else:
        return "unknown"  # har doim string qaytaradi


# --- 2) Track click va redirect lead form ---
def track_click(request):
    video_id = request.GET.get("video_id", "")
    source = detect_source(request)

    Click.objects.create(
        source=source,
        # Agar Click modelda video maydon bo‘lsa:
        # video=video_id
    )

    return redirect(f"/analytics/lead-form/?source={source}&video={video_id}")


# --- 3) Lead form ---
def lead_form(request):
    if request.method == "POST":
        name = request.POST.get("name")
        number = request.POST.get("number")
        source = request.POST.get("source", "unknown")
        course = request.POST.get("course", "")

        Lead.objects.create(
            full_name=name,
            phone=number,
            source=source,
            course=course
        )

        return redirect("/analytics/thanks/")

    # GET bo‘lsa, formni ko‘rsatish
    source = request.GET.get("source", "unknown")
    video = request.GET.get("video", "")
    return render(request, "lead_form.html", {"source": source, "video": video})


# --- 4) Thanks page ---
def thanks(request):
    return render(request, "thanks.html")


# --- 5) Click statistikasi (JSON) ---
def click_stats(request):
    data = (
        Click.objects
        .values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return JsonResponse(list(data), safe=False)


# --- 6) Stats page (HTML) ---
def stats_page(request):
    return render(request, "stats.html")
