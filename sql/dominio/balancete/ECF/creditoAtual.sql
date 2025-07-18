SELECT
    contaLancamento = CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO,
    credito_atual = SUM(bethadba.ctlancto.vlor_lan)
FROM
    bethadba.CTLANCTO_SPED_ECF_GERAL
    
INNER JOIN bethadba.ctlancto ON 
    ctlancto.codi_emp = CTLANCTO_SPED_ECF_GERAL.CODI_EMP AND
    ctlancto.nume_lan = CTLANCTO_SPED_ECF_GERAL.NUME_LAN
    
WHERE
    CTLANCTO_SPED_ECF_GERAL.CODI_EMP = :codi_emp AND
    CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO <> 0 AND
    CTLANCTO.CCRE_LAN <> 0 AND
    ctlancto.data_lan BETWEEN :data_inicial AND :data_final AND
    ( :zeramento = 'N' OR ( :zeramento = 'S' AND ctlancto.orig_lan <> 2)) AND
    ( :transferencia = 'N' OR ( :transferencia = 'S' AND ctlancto.orig_lan <> 34))
    
GROUP BY
    contaLancamento
