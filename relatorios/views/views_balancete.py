from django.shortcuts import render, redirect

from sql.utils.sql_utils import sql_para_dataframe

# ESTOU IMPORTANDO UMA FUNÇÃO PARA SE CONECTAR AOS BANCOS EXISTENTES DA DOMINIO

from relatorios.utils.conexao import conectar_dominio

# FORM BASE (BOA PARTE DOS RELATORIOS PRECISAM DESSES INPUTS)


# ESTOU IMPORTANDO DUAS FUNÇÕES QUE RETORNAM UM DATAFRAME (BALANCETE, BALANCETE ECF)

from relatorios.utils.balancete_utils import relatorioBalanceteDominio, relatorioBalanceteECF

# ESTOU IMPORTANDO UMA FUNÇÃO PARA FICAR FORMANTANDO DE MANEIRA MAIS INTUITIVA. 

from relatorios.utils.competencias import formata_data

# ESTOU IMPORTANDO MEU FORMULARIO

from relatorios.forms.formularios import BalanceteForm

def balancete_relatorio_view(request):
    
    # REQUISIÇÃO (GET), QUANDO ESTÃO TENTANDO ACESSAR O FORM.
    if request.method == 'GET':
        
        # ENVIA O FORMULARIO "BalanceteForm"
        
        form = BalanceteForm()
        
        # ENGLOBA EM UM DICT COM O FORMULARIO E UM TITLE
        
        contexto = {
            'form': form,
            'form_title': form.titulo,
        }
        
        # RENDERIZA O HTML, MANDANDO O DICIONARIO PYTHON COM AS INFORMAÇÕES
        
        return render(
            request, 
            'relatorios/balancete/form.html', 
            contexto
        )

    # ELE IRÁ VER SE MEU FORMULARIO FOI MANDADO CORRETAMENTE, CASO CONTRARIO ELE IRÁ MANDAR O FORMULARIO NOVAMENTE, MAS DESSA VEZ COM OS ERROS)
    
    form = BalanceteForm(request.POST)
    if not form.is_valid():

        contexto = {
            'form': form,
            'form_title': form.titulo
        }

        return render(
            request, 
            'relatorios/balancete/form.html',
            contexto
        )
    
    # DADOS DO FORMULARIO
    
    # ESTOU APENAS PEGANDO OS DADOS DO USUARIO.
    
    dados = form.cleaned_data
    tipo_balancete = dados['balancete_tipo']
    codigo_empresa = dados['codigo_empresa']
    banco_id = dados['conexao']
    data_inicial = dados['data_inicial']
    data_final =  dados['data_final']
    transferencia = 'S' if dados.get('transferencia') else 'N'
    zeramento = 'S' if dados.get('zeramento') else 'N'
    cruzamento_ecf = 'S' if dados.get('cruzamento_ecf') else 'N'
    mostrar_resumo = dados.get('resumo', False)
    empresa =  getattr(form, 'empresa', None) # ESTOU PEGANDO UM ATRIBUTO DEFINIDO LA NO FORM, VISTO QUE LA EU JA CONSULTO A EMPRESA PARA VALIDAÇÃO.
    
    cnpj = empresa['CNPJ']
    nome_empresa = empresa['nome_emp']
    mostrar_conferencia= dados.get('conferencia', False)

    # FORMATANDO PARA A DATA QUE VEM '2024-01-01' DOS INPUTS E DEIXANDO '01/01/2024' PARA QUE POSSARMOS INSERIR NO HTML.
    
    data_inicial_formatado = formata_data(dados['data_inicial'], '%Y-%m-%d', '%d/%m/%Y')
    data_final_formatado =  formata_data(dados['data_final'], '%Y-%m-%d', '%d/%m/%Y')
    
    # ME CONECTANDO AO BANCO DE DADOS SELECIONADO.
    
    conexao = conectar_dominio(banco_id)
    
    # ESTOU EXECUTANDO A FUNÇÃO DEPENDENDO DO RELATORIO DESEJADO.

    if tipo_balancete == 'normal':
        df_relatorio = relatorioBalanceteDominio(
            codigo_empresa, data_inicial, data_final,
            zeramento, transferencia, conexao, cruzamento_ecf
        )
    else:
        df_relatorio = relatorioBalanceteECF(
            codigo_empresa, data_inicial, data_final,
            zeramento, transferencia, conexao
        )


    contexto = {
        'dados_relatorio_balancete': df_relatorio.to_dict(orient='records'),
        'data_inicial': data_inicial_formatado,
        'data_final': data_final_formatado,
        'nome_empresa': nome_empresa,
        'cnpj': cnpj,
        'form_title': form.titulo,
        'mostrar_resumo': mostrar_resumo,
        'cruzamento_ecf': cruzamento_ecf,
        'mostrar_conferencia': mostrar_conferencia,
        # 'resumo_dados': df_relatorio.to_dict(orient='records')
    }
    
    return render(
        request, 
        'relatorios/balancete/result.html', 
        contexto
    )   