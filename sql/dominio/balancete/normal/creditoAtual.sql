SELECT
    contaLancamento = bethadba.ctlancto.ccre_lan,
    credito_atual = SUM(bethadba.ctlancto.vlor_lan)
FROM
    bethadba.ctlancto
    
WHERE
    bethadba.ctlancto.codi_emp = :codi_emp AND
    bethadba.ctlancto.data_lan BETWEEN :data_inicial AND :data_final AND
    bethadba.ctlancto.ccre_lan <> 0 AND
    ( :zeramento = 'N' OR ( :zeramento = 'S' AND ctlancto.orig_lan <> 2)) AND
    ( :transferencia = 'N' OR ( :transferencia = 'S' AND ctlancto.orig_lan <> 34))

GROUP BY
    contaLancamento