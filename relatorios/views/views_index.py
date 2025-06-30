from django.shortcuts import render
from django.views import View


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "relatorios/index.html")

    # Se precisar de método post também
    def post(self, request, *args, **kwargs):
        return render(request, "relatorios/index.html")
