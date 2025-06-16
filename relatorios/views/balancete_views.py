from django.shortcuts import render, redirect
from django.http import JsonResponse
from relatorios.utils.balancete_utils import relatorioBalanceteDominio, relatorioBalanceteECF
from relatorios.utils.conexao import conectar_dominio
from relatorios.utils.competencias import formata_data

def pesquisa(request):
    if request.method == 'GET':
        return render(request, 'relatorios/balancete/balancete_form.html')
    
    # TRATATIVAS DO POST\
    
    tipo_balancete = request.POST.get('balancete_tipo')
    empresa = request.POST.get('empresa')
    banco = request.POST.get('conexao')
    data_inicial = request.POST.get('dataInicial')
    data_final = request.POST.get('dataFinal')
    transferencia = 'S' if request.POST.get('transferencia') else 'N'
    zeramento = 'S' if request.POST.get('zeramento') else 'N'

    conexao = conectar_dominio(banco)
    
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

    relatorio = relatorio.rename(columns={
        "Saldo Anterior": "saldo_anterior",
        "debitoAtual": "debito_atual",
        "creditoAtual": "credito_atual",
        "Saldo Atual": "saldo_atual"
    })

    relatorio_json = relatorio.to_dict(orient='records')

    request.session['relatorio_json'] = relatorio_json
    request.session['data_inicial'] = data_inicial
    request.session['data_final'] = data_final

    return redirect('relatorios:resultado')


def resultado(request):
    
    relatorio_json = request.session.get('relatorio_json', [])
    
    if not relatorio_json:
        return redirect('relatorios:pesquisa')
    
    data_inicial = request.session.get('data_inicial')
    data_final = request.session.get('data_final')

    data_inicial_formatada = formata_data(data_inicial, '%Y-%m-%d', '%d/%m/%Y')
    data_final_formatada = formata_data(data_final, '%Y-%m-%d', '%d/%m/%Y')

    # NÃO DELETAR (ISSO É PARA SER UTILIZADO NO FUTURO, POREM PARA DEBUGAR A APLICAÇÃO ISSO ATRAPALHA) 
    # request.session.pop('relatorio_json', None)
    # request.session.pop('data_inicial', None)
    # request.session.pop('data_final', None)

    return render(request, 'relatorios/balancete/balancete_result.html', {
        'relatorio_json': relatorio_json,
        'data_inicial': data_inicial_formatada,
        'data_final': data_final_formatada

    })


