SELECT DISTINCT
    bethadba.ctlancto.ccre_lan AS "contaLancamento",
    (
        SELECT bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO
        FROM bethadba.CTLANCTO_SPED_ECF_GERAL
        WHERE bethadba.CTLANCTO_SPED_ECF_GERAL.codi_emp = bethadba.ctlancto.codi_emp
          AND bethadba.CTLANCTO_SPED_ECF_GERAL.nume_lan = bethadba.ctlancto.nume_lan
          AND bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO <> 0
    ) AS "contaLancamento_ECF"
    
FROM bethadba.ctlancto
WHERE bethadba.ctlancto.codi_emp = :codi_emp
  AND bethadba.ctlancto.data_lan BETWEEN :data_inicial AND :data_final AND
  bethadba.ctlancto.ccre_lan <> 0 
