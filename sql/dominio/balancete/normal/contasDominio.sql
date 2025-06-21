SELECT
    contaLancamento = bethadba.ctcontas.codi_cta,
    classificacaoConta = bethadba.ctcontas.clas_cta,
    descricaoConta = bethadba.ctcontas.nome_cta,
    tipoConta = bethadba.ctcontas.tipo_cta  
FROM
    bethadba.ctcontas
    
WHERE
    bethadba.ctcontas.codi_emp = :codi_emp