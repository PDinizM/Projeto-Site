from django import forms

class BasePesquisaForm(forms.Form):
    
    # Conexões Possiveis
    
    CONEXOES = [
        ('banco1', 'Banco 1'),
        ('banco2', 'Banco 2'),
        ('banco3', 'Banco 3'),
        ('banco4', 'Banco 4'),
    ]

    # Fields 

    conexao = forms.ChoiceField(
        choices=CONEXOES,
        widget=forms.RadioSelect,
        label='Conexão'
    )
    
    dataInicial = forms.DateField(
        label='Data Inicial',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    dataFinal = forms.DateField(
        label='Data Final',
        widget=forms.DateInput(attrs={'type': 'date'})
    )


class PesquisaForm(BasePesquisaForm):

    # Tipos de Balancete
    
    TIPOS_BALANCETE = [
        ('normal', 'Balancete Normal'),
        ('plano_referencial', 'Balancete Plano Referencial'),
    ]
    
    # Fields 

    balancete_tipo = forms.ChoiceField(
        choices=TIPOS_BALANCETE,
        widget=forms.RadioSelect,
        label='Tipo de Balancete'
    )

    zeramento = forms.BooleanField(
        required=False,
        label='Desconsiderar Zeramento'
    )

    transferencia = forms.BooleanField(
        required=False,
        label='Desconsiderar Transferência De Lucro/Prejuízo'
    )
