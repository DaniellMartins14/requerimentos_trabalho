from db import execute_one

# Se o .env, o XAMPP ou o banco estiverem incorretos, o erro aparece aqui.
print("Conectado ao banco de dados.")

info = execute_one(
    "SELECT DATABASE() AS banco, VERSION() AS versao, NOW() AS agora"
)
print("Banco:", info["banco"])
print("Servidor:", info["versao"])
print("Hora do banco:", info["agora"])

municipes = execute_one(
    "SELECT COUNT(*) AS total FROM municipes WHERE deletado_em IS NULL"
)
processos = execute_one(
    "SELECT COUNT(*) AS total FROM processos WHERE deletado_em IS NULL"
)
inscricoes = execute_one(
    "SELECT COUNT(*) AS total FROM inscricoes_municipais WHERE deletado_em IS NULL"
)

print("Tabela municipes:", municipes["total"], "linhas")
print("Tabela processos:", processos["total"], "linhas")
print("Tabela inscricoes_municipais:", inscricoes["total"], "linhas")
