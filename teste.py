from relatorios.utils.conexao import conectar_dominio

conexao = conectar_dominio("Banco 1")

print(conexao.pool.status())
