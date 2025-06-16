from django.urls import path
from controller import views

app_name = 'controller'

urlpatterns = [
    path('', views.index, name='index'),
    
    
    # Empresas (CRUD)
    path('<int:empresa_id>/', views.empresa, name='empresa'),
    path('create/', views.create, name='create'),
]

