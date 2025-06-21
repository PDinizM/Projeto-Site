SELECT DISTINCT
    bethadba.ctlancto.cdeb_lan AS "contaLancamento",
    (
        SELECT bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO
        FROM bethadba.CTLANCTO_SPED_ECF_GERAL
        WHERE bethadba.CTLANCTO_SPED_ECF_GERAL.codi_emp = bethadba.ctlancto.codi_emp
          AND bethadba.CTLANCTO_SPED_ECF_GERAL.nume_lan = bethadba.ctlancto.nume_lan
          AND bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO <> 0
    ) AS "contaLancamento_ECF"
    
FROM bethadba.ctlancto
WHERE bethadba.ctlancto.codi_emp = :codi_emp
  AND bethadba.ctlancto.data_lan BETWEEN :data_inicial AND :data_final AND
  bethadba.ctlancto.cdeb_lan <> 0 
