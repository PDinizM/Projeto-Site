SELECT
    conta_lancamento = bethadba.ctcontas.codi_cta,
    classificacao_conta = bethadba.ctcontas.clas_cta,
    descricao_conta = bethadba.ctcontas.nome_cta,
    tipo_conta = bethadba.ctcontas.tipo_cta  
FROM
    bethadba.ctcontas
    
WHERE
    bethadba.ctcontas.codi_emp = :codi_emp