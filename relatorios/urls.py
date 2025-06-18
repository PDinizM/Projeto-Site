from django.urls import path
from relatorios import views

app_name = 'relatorios'

urlpatterns = [
    
    # AQUI PODERÁ TER UM MENU COM VARIOS CARD LINKANDO AOS RELATORIOS 
    
    path('balancete/', views.balancete_relatorio_view, name='balancete_relatorio_view'),
    
    # AQUI TERÁ AS URLS DOS RELATORIOS, (BALANCETE, RAZAO, COMPARATIVO, CONTA VIRANDO)
    # path('balancete/', views.balancete_resultado_view, name='balancete_resultado_view'),
    # path('teste/', views.teste, name='teste'),
    # path('teste2/', views.teste2, name='teste'),
]

