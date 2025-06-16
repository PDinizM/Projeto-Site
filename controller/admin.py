from django.contrib import admin
from controller import models

@admin.register(models.Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = 'nome_empresarial',
    
@admin.register(models.Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = 'nome_equipe',

