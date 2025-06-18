from django.shortcuts import render, redirect

# ESTOU IMPORTANDO DUAS FUNÇÕES QUE RETORNAM UM DATAFRAME (BALANCETE, BALANCETE ECF)

from relatorios.utils.balancete_utils import relatorioBalanceteDominio, relatorioBalanceteECF

# ESTOU IMPORTANDO UMA FUNÇÃO PARA SE CONECTAR AOS BANCOS EXISTENTES DA DOMINIO
from relatorios.utils.conexao import conectar_dominio

# ESTOU IMPORTANDO UMA FUNÇÃO PARA FICAR FORMANTANDO DE MANEIRA MAIS INTUITIVA. 
from relatorios.utils.competencias import formata_data

# ESTOU IMPORTANDO MEU FORMULARIO
from relatorios.forms.formularios import BalanceteForm

# ESTOU IMPORTANDO UMA FUNÇÃO QUE LÊ ARQUIVOS .SQL E O EXECUTAM RETORNANDO UM DATAFRAME.

from sql.utils.sql_utils import sql_para_dataframe

def balancete_relatorio_view(request):
    
    # REQUISIÇÃO (GET), QUANDO ESTÃO TENTANDO ACESSAR O FORM.
    if request.method == 'GET':
        
        # ENVIA O FORMULARIO "BalanceteForm"
        
        form = BalanceteForm()
        
        # ENGLOBA EM UM DICT COM O FORMULARIO E UM TITLE
        
        contexto = {
            'form': form,
            'title': 'Balancete'
        }
        
        # RENDERIZA O HTML, MANDANDO O DICIONARIO PYTHON COM AS INFORMAÇÕES
        
        return render(
            request, 
            'relatorios/balancete/balancete_form.html', 
            contexto
        )

    # CASO NAO SEJA "GET", SERÁ POST. (NÃO CRIEI UM IF PARA QUE NAO FICASSE MUITO IDENTADO)
    # VERIFICA OS DADOS DO POST NO FORMULARIO
    # ELE IRÁ VER SE MEU FORMULARIO FOI MANDADO CORRETAMENTE, CASO CONTRARIO ELE IRÁ MANDAR O FORMULARIO NOVAMENTE, MAS DESSA VEZ COM OS ERROS)
    
    form = BalanceteForm(request.POST)
    if not form.is_valid():

        contexto = {
            'form': form,
            'title': 'Balancete'
        }

        return render(
            request, 
            'relatorios/balancete/balancete_form.html',
            contexto
        )
    
    # DADOS DO FORMULARIO
    
    # ESTOU APENAS PEGANDO OS DADOS DO USUARIO.
    
    dados = form.cleaned_data
    tipo_balancete = dados['balancete_tipo']
    codigo_empresa = dados['empresa']
    banco_id = dados['conexao']
    data_inicial = dados['data_inicial']
    data_final =  dados['data_final']
    transferencia = 'S' if dados.get('transferencia') else 'N'
    zeramento = 'S' if dados.get('zeramento') else 'N'
    
    # FORMATANDO PARA A DATA QUE VEM '2024-01-01' DOS INPUTS E DEIXANDO '01/01/2024' PARA QUE POSSARMOS INSERIR NO HTML.
    
    data_inicial_formatado = formata_data(dados['data_inicial'], '%Y-%m-%d', '%d/%m/%Y')
    data_final_formatado =  formata_data(dados['data_final'], '%Y-%m-%d', '%d/%m/%Y')
    
    # ME CONECTANDO AO BANCO DE DADOS SELECIONADO.
    
    conexao = conectar_dominio(banco_id)
    
    # CONSULTANDO UM RELATORIO SQL QUE RETORNA ALGUNS DADOS DA EMPRESA.

    consulta_empresa = sql_para_dataframe(
        'dominio/empresas.sql',
        conexao,
        codigo_empresa
        )
    
    # AQUI VALIDA SE A EMPRESA INSERIDA DE FATO EXISTE.
        
    if consulta_empresa.empty:
        form.add_error('empresa', 'Empresa não encontrada no banco de dados.')
        return render(request, 'relatorios/balancete/balancete_form.html', {
            'form': form,
            'title': 'Balancete'
        })
        
    # PEGANDO A PRIMEIRA LINHA DO RESULTADO:
    empresa = consulta_empresa.squeeze()
            
    # COLETANDO OS DADOS QUE EU QUERO
    
    cnpj = empresa['CNPJ']
    nome_empresa = empresa['nome_emp']
    

    # ESTOU EXECUTANDO A FUNÇÃO DEPENDENDO DO RELATORIO DESEJADO.

    if tipo_balancete == 'normal':
        df_relatorio = relatorioBalanceteDominio(
            codigo_empresa, data_inicial, data_final,
            zeramento, transferencia, conexao
        )
    else:
        df_relatorio = relatorioBalanceteECF(
            codigo_empresa, data_inicial, data_final,
            zeramento, transferencia, conexao
        )
    
    # FECHANDO A CONEXÃO
    
    conexao.close()
    
    contexto = {
        'dados_relatorio_balancete': df_relatorio.to_dict(orient='records'),
        'data_inicial': data_inicial_formatado,
        'data_final': data_final_formatado,
        'nome_empresa': nome_empresa,
        'cnpj': cnpj,
    }
    
    return render(
        request, 
        'relatorios/balancete/balancete_result.html', 
        contexto
    )   