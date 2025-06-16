from django.shortcuts import render, redirect, get_object_or_404
from controller.models import Empresa


def index(request):
    
    empresas = Empresa.objects.all()    
    
    dados = {
        'empresas': empresas
    }
    
    return render(
        request, 
        'controller/index.html',
        dados
    )
    

def empresa(request, empresa_id):
    
    empresa = get_object_or_404(Empresa, pk=empresa_id)

    return render(
        request,
        'controller/empresa.html',
        {'empresa': empresa}
    )

    
    
