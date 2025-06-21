SELECT
    contaLancamento = bethadba.ctlancto.cdeb_lan,
    debitoAnterior = SUM(bethadba.ctlancto.vlor_lan)
FROM
    bethadba.ctlancto
    
WHERE
    bethadba.ctlancto.codi_emp = :codi_emp AND
    bethadba.ctlancto.data_lan < :data_inicial AND
    bethadba.ctlancto.cdeb_lan <> 0 

GROUP BY
    contaLancamento