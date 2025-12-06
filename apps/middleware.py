# middleware.py
class UTMMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Foydalanuvchi GET params orqali kelgan utm_source va utm_campaignni olamiz
        utm_source = request.GET.get("utm_source")
        utm_campaign = request.GET.get("utm_campaign")

        # Agar bor bo‘lsa, sessionga saqlaymiz
        if utm_source:
            request.session["utm_source"] = utm_source
        if utm_campaign:
            request.session["utm_campaign"] = utm_campaign

        # Keyingi viewga requestni yuboramiz
        response = self.get_response(request)
        return response

