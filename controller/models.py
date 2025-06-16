from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from utils.validate_cnpj import validate_cnpj

class Empresa(models.Model):
    
    cnpj = models.CharField(max_length=14, unique=True, verbose_name="CNPJ")
    nome_empresarial = models.CharField(max_length=255, verbose_name="Nome Empresarial")
    data_abertura = models.DateField(blank=True, null=True, verbose_name="Data de Abertura")
    # situacao_cnpj = foreign key
    cep = models.CharField(max_length=8, blank=True, verbose_name="CEP")
    logradouro = models.CharField(max_length=255, blank=True)
    # uf = foreign key
    complemento = models.CharField(max_length=255, blank=True)
    data_situacao = models.DateField(blank=True, null=True, verbose_name="Data da Situação")
    numero_endereco = models.IntegerField(blank=True, null=True, verbose_name="Número (Endereço)")
    bairro = models.CharField(max_length=50, blank=True)
    # municipio = foreign key
    # Equipe - Contábil
    # Equipe - DP
    servico_juridico = models.BooleanField(default=False, verbose_name="Serviço Júridico")
    servico_contabil = models.BooleanField(default=False, verbose_name="Serviço Contábil")
    servico_dp = models.BooleanField(default=False, verbose_name="Serviço Departamento Pessoal")
    
    equipe_responsavel = models.ForeignKey('Equipe', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Equipe Responsável")
    
    def __str__(self):
        return self.nome_empresarial
    
    def clean(self):
        validate_cnpj(self.cnpj)
        
        
class Equipe(models.Model):
    
    nome_equipe = models.CharField(max_length=50)
    
    membros = models.ManyToManyField(User, related_name='equipes')

    def __str__(self):
        return self.nome_equipe


    
    