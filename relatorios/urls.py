from django.urls import path
from relatorios import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.pesquisa, name='pesquisa'),
    path('balancete/', views.resultado, name='resultado')
]

