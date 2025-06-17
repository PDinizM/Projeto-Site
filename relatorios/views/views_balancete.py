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

# ESSA VIEW SERA MODIFICADA ASSIM QUE FOR IMPLEMENTADO O FORM VIA OBJECT FORM (O NOVO VIEW ESTA COM O NOME DE "view_exemplo")
def balancete_relatorio_view(request):
    
    # REQUISIÇÃO (GET), QUANDO ESTÃO TENTANDO ACESSAR O FORM.
    if request.method == 'GET':
        
        # ENVIA O FORMULARIO "BalanceteForm"
        
        form = BalanceteForm()
        
        # ENGLOBA EM UM DICT (AQUI EU MANDO O FORM, ATUALMENTE NAO ESTÁ SENDO UTILIZADO MAS IREMOS IMPLEMENTAR).
        
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

    dados = {k: v[0] if isinstance(v, list) else v for k, v in request.POST.lists()}

    tipo_balancete = dados['balancete_tipo']
    empresa = dados['empresa']
    banco = dados['conexao']
    data_inicial = dados['dataInicial']
    data_final = dados['dataFinal']
    transferencia = 'S' if dados.get('transferencia') else 'N'
    zeramento = 'S' if dados.get('zeramento') else 'N'


    conexao = conectar_dominio(banco)
        
    consulta_empresa = sql_para_dataframe(
        'dominio/empresas.sql',
        conexao,
        empresa
        ).iloc[0]
    
    cnpj = consulta_empresa['CNPJ']
    nome_empresa = consulta_empresa['nome_emp']
    

    if tipo_balancete == 'normal':
        relatorio = relatorioBalanceteDominio(
            empresa, data_inicial, data_final,
            zeramento, transferencia, conexao
    )
    elif tipo_balancete == 'plano_referencial':
        relatorio = relatorioBalanceteECF(
            empresa, data_inicial, data_final,
            zeramento, transferencia, conexao
    )

    dados_relatorio_balancete = relatorio.to_dict(orient='records')

    request.session['dados_relatorio_balancete'] = dados_relatorio_balancete
    request.session['data_inicial'] = data_inicial
    request.session['data_final'] = data_final
    request.session['nome_empresa'] = nome_empresa
    request.session['cnpj'] = cnpj

    return redirect('relatorios:balancete_resultado_view')


def balancete_resultado_view(request):
    
     # ESSE CODIGO NAO ESTÁ IMPLEMENTADO AINDA POR CONTA DO FORMULARIO MANUAL]
     
    # PEGA OS DADOS ARMAZENADOS NA SESSÃO PROVINIENTES DA MINHA VIEW PESQUISA.
     
    #  contexto = request.session.get('balancete_contexto')

    # Caso alguem tente acessar o relatorio sem ter uma sessão preenchida já, irá ser redirecionado ao formulario.
    
    # if not contexto:
    #     return redirect('relatorios:balancete_relatorio_view')
    
    dados_relatorio_balancete = request.session.get('dados_relatorio_balancete', [])
    
    if not dados_relatorio_balancete:
        return redirect('relatorios:balancete_pesquisa_view')
    
    data_inicial = request.session.get('data_inicial')
    data_final = request.session.get('data_final')
    nome_empresa = request.session.get('nome_empresa')
    cnpj = request.session.get('cnpj')

    data_inicial_formatada = formata_data(data_inicial, '%Y-%m-%d', '%d/%m/%Y')
    data_final_formatada = formata_data(data_final, '%Y-%m-%d', '%d/%m/%Y')

    return render(request, 'relatorios/balancete/balancete_result.html', {
        'dados_relatorio_balancete': dados_relatorio_balancete,
        'data_inicial': data_inicial_formatada,
        'data_final': data_final_formatada,
        'cnpj': cnpj,
        'nome_empresa': nome_empresa,
    })


def teste(request):
    if request.method == 'POST':
        form = BalanceteForm(request.POST)
        if form.is_valid():
            # Acessa os dados do formulário limpos
            dados = form.cleaned_data
            # Você pode agora usar esses dados para consultas, relatórios etc.
            # Exemplo: dados['dataInicial'], dados['conexao'], etc.
            return render(request, 'teste.html', {'form': form})

    else:
        form = BalanceteForm()
    
    return render(request, 'teste.html', {'form': form})


def teste2(request):
    if request.method == 'POST':
        form = BalanceteForm(request.POST)
        if form.is_valid():
            # Acessa os dados do formulário limpos
            dados = form.cleaned_data
            # Você pode agora usar esses dados para consultas, relatórios etc.
            # Exemplo: dados['dataInicial'], dados['conexao'], etc.
            return render(request, 'relatorios/balancete/teste2.html', {'form': form})

    else:
        form = BalanceteForm()
    return render(request, 'relatorios/balancete/teste2.html', {'form': form})    


def view_exemplo(request):
    
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
        return render(
            request, 
            'relatorios/balancete/balancete_form.html',
            contexto
        )

    # DADOS DO FORMULARIO
    
    # ESTOU APENAS PEGANDO OS DADOS DO USUARIO E INSERINDO NA MINHA FUNÇÃO.
    
    dados = form.cleaned_data
    tipo_balancete = dados['balancete_tipo']
    codigo_empresa = dados['empresa']
    banco_id = dados['conexao']
    data_inicial = formata_data(dados['dataInicial'], '%Y-%m-%d', '%d/%m/%Y')
    data_final =  formata_data(dados['dataFinal'], '%Y-%m-%d', '%d/%m/%Y')
    transferencia = 'S' if dados.get('transferencia') else 'N'
    zeramento = 'S' if dados.get('zeramento') else 'N'
    
    # ME CONECTANDO AO BANCO DE DADOS SELECIONADO.
    
    conexao = conectar_dominio(banco_id)
    
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

    # CONSULTANDO UM RELATORIO SQL QUE RETORNA DADOS DA EMPRESA

    consulta_empresa = sql_para_dataframe(
        'dominio/empresas.sql',
        conexao,
        codigo_empresa
        ).iloc[0]
    
    # FECHANDO A CONEXÃO
    
    conexao.close()
    
    # COLETANDO OS DADOS QUE EU QUERO
    
    cnpj = consulta_empresa['CNPJ']
    nome_empresa = consulta_empresa['nome_emp']

    contexto = {
        'dados': df_relatorio.to_dict(orient='records'),
        'data_inicial': data_inicial,
        'data_final': data_final,
        'nome_empresa': nome_empresa,
        'cnpj': cnpj,
    }
    
    return render(
        request, 
        'relatorios/balancete/balancete_result.html', 
        contexto
    )   