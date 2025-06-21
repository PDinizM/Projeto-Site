# REGRA DE CLASSIFICAÇÃO DA ECF

def regraClassificacaoECF(classificacao):
    
    if len(classificacao) == 1:
        return classificacao
    elif len(classificacao) == 3:
        return classificacao[:1] + '.' + classificacao[1:3]
    elif len(classificacao) == 5:
        return classificacao[:1] + '.' + classificacao[1:3] + '.' + classificacao[3:5]
    elif len(classificacao) == 7:
        return classificacao[:1] + '.' + classificacao[1:3] + '.' + classificacao[3:5] + '.' + classificacao[5:7]
    elif len(classificacao) == 9:
        return classificacao[:1] + '.' + classificacao[1:3] + '.' + classificacao[3:5] + '.' + classificacao[5:7] + '.' + classificacao[7:9]
    elif len(classificacao) == 11:
        return classificacao[:1] + '.' + classificacao[1:3] + '.' + classificacao[3:5] + '.' + classificacao[5:7] + '.' + classificacao[7:9] + '.' + classificacao[9:11]

# REGRA DE CLASSIFICAÇÃO DA DOMINIO

def regraClassificacaoDominio(classificacao):

    if len(classificacao) == 1:
        return classificacao
    elif len(classificacao) == 2:
        return classificacao[:1] + '.' + classificacao[1:2]
    elif len(classificacao) == 3:
        return classificacao[:1] + '.' + classificacao[1:2] + '.' + classificacao[2:3]
    elif len(classificacao) == 5:
        return classificacao[:1] + '.' + classificacao[1:2] + '.' + classificacao[2:3] + '.' + classificacao[3:5]
    elif len(classificacao) >= 5:
        return classificacao[:1] + '.' + classificacao[1:2] + '.' + classificacao[2:3] + '.' + classificacao[3:5] + '.' + classificacao[5:]
