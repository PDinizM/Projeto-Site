from django import forms

# ESTOU IMPORTANDO UMA FUNÇÃO QUE LÊ ARQUIVOS .SQL E O EXECUTAM RETORNANDO UM DATAFRAME.

from sql.utils.sql_utils import sql_para_dataframe

# ESTOU IMPORTANDO UMA FUNÇÃO PARA SE CONECTAR AOS BANCOS EXISTENTES DA DOMINIO

from relatorios.utils.conexao import conectar_dominio, CONEXOES_DOMINIO

# FORM BASE (BOA PARTE DOS RELATORIOS PRECISAM DESSES INPUTS)

class BasePesquisaForm(forms.Form):
    
    # Fields 

    conexao = forms.ChoiceField(
        choices=[(c, c) for c in CONEXOES_DOMINIO],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Conexão',
        required=True,
        initial="Banco 1"
    )
    
    codigo_empresa = forms.CharField(
        label='Empresa',
        required=True,
        help_text='Informe uma lista de empresas separada por vírgulas (Ex: 1,2,3).',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9]*',
            'placeholder': 'Digite apenas números',
        }
        ),
    )

    data_inicial = forms.DateField(
        label='Data Inicial',
        widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
        required=True
    )

    data_final = forms.DateField(
        label='Data Final',
        widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}),
        required=True
    )
    
    # CHAMANDO A FUNÇÃO CLEAN PARA CRIAR AS VALIDAÇÕES    

    def clean(self):
        
        # PEGANDO OS DADOS QUE EU IREI VALIDAR
        
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get('data_inicial')
        data_final = cleaned_data.get('data_final')
        codigo_empresa = cleaned_data.get('codigo_empresa')
        conexao = cleaned_data.get('conexao')
        
        # 1º VALIDAÇÃO PARA QUE A DATA_FINAL NAO SEJA MENOR QUE A DATA_INICIAL
        if data_inicial and data_final and data_final < data_inicial:
            self.add_error('data_final', "A data final não pode ser menor que a data inicial.")

        # 2º VALIDAÇÃO VERIFICA SE A EMPRESA EXISTE NO BANCO DE DADOS
        if codigo_empresa and conexao:
            conexao_db = conectar_dominio(conexao)
            df = sql_para_dataframe('dominio/empresas.sql', conexao_db, codigo_empresa)
            conexao_db.close()

            if df.empty:
                self.add_error('codigo_empresa', 'Empresa não encontrada no banco de dados.')
            else:
                self.empresa = df.squeeze()


# FORM ESPECIFICO DO BALANCETE, HERDA OS INPUTS DA BASE E INCREMENTA OS PROPRIOS.
class BalanceteForm(BasePesquisaForm):
    
    titulo = 'Balancete'
    
    # Tipos de Balancete
    TIPOS_BALANCETE = [
        ('normal', 'Balancete Normal'),
        ('plano_referencial', 'Balancete Plano Referencial'),
    ]
    
    # Fields
    
    # Field Tipo Balancete
    balancete_tipo = forms.ChoiceField(
        choices=TIPOS_BALANCETE,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Tipo de Balancete',
        initial="normal"
    )
    
    # FIELDS OPÇÕES
    
    # Field Zeramento
    zeramento = forms.BooleanField(
        label='Desconsiderar Zeramento',
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )
    
    # Field Transferencia
    transferencia = forms.BooleanField(
        label='Desconsiderar Transferência De Lucro/Prejuízo',
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )
    
    consolidado = forms.BooleanField(
        label='Emitir Balancete Consolidado',
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )
    
    conferencia = forms.BooleanField(
        label='Emitir Coluna Conferência',
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )
    
    resumo = forms.BooleanField(
        label='Emitir Resumo Final',
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )
