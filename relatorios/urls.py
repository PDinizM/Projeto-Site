from django.urls import path

from .views.balancete import BalanceteRelatorioView
from .views.comparativo import ComparativoRelatorioView
from .views.razao import RazaoRelatorioView
from .views.views_index import IndexView

app_name = "relatorios"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("balancete/", BalanceteRelatorioView.as_view(), name="balancete"),
    path("comparativo/", ComparativoRelatorioView.as_view(), name="comparativo"),
    path("razao/", RazaoRelatorioView.as_view(), name="razao"),
    # AQUI PODERÁ TER UM MENU COM VARIOS CARD LINKANDO AOS RELATORIOS
    # path("balancete/", views.balancete_relatorio_view, name="balancete_relatorio_view"),
    # AQUI TERÁ AS URLS DOS RELATORIOS, (BALANCETE, RAZAO, COMPARATIVO, CONTA VIRANDO)
    # path('balancete/', views.balancete_resultado_view, name='balancete_resultado_view'),
    # path('teste/', views.teste, name='teste'),
    # path('teste2/', views.teste2, name='teste'),
]
