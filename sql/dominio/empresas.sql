SELECT
	bethadba.geempre.codi_emp,
	bethadba.geempre.nome_emp,
	bethadba.geempre.esta_emp,
	bethadba.geempre.iest_emp,
    CNPJ = 
        CASE
            WHEN bethadba.geempre.tins_emp = 1 THEN
                SUBSTRING(bethadba.geempre.cgce_emp,1,2) + '.' +
                SUBSTRING(bethadba.geempre.cgce_emp,3,3) + '.' +
                SUBSTRING(bethadba.geempre.cgce_emp,6,3) + '/' +
                SUBSTRING(bethadba.geempre.cgce_emp,9, 4) + '-' +            
                SUBSTRING(bethadba.geempre.cgce_emp,13, 2)
            WHEN bethadba.geempre.tins_emp = 2 THEN
                SUBSTRING(bethadba.geempre.cgce_emp,1,3) + '.' +
                SUBSTRING(bethadba.geempre.cgce_emp,4,3) + '.' +
                SUBSTRING(bethadba.geempre.cgce_emp,7,3) + '-' +
                SUBSTRING(bethadba.geempre.cgce_emp,10,2)
            ELSE
                bethadba.geempre.cgce_emp
        END
FROM
    bethadba.geempre
WHERE
    bethadba.geempre.codi_emp IN :lista_empresas