"""Acesso ao banco MySQL do Cadastro de Municipes.

As configuracoes sao lidas do arquivo .env. O modulo centraliza
as conexoes e as consultas usadas pelas rotas Flask.
"""

import os

from dotenv import load_dotenv
from mysql.connector import Error, pooling

# Carrega as variaveis locais antes de montar a configuracao.
load_dotenv()

if os.getenv("DB_NAME") is None:
    raise RuntimeError(
        "Nao encontrei o arquivo .env. Copie .env.example para .env e preencha."
    )

CONFIGURACAO = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4",
    "time_zone": "-03:00",
    "use_pure": True,
}

# Pool reutilizavel: evita abrir uma conexao nova a cada consulta.
pool = pooling.MySQLConnectionPool(
    pool_name="cadastro_municipes_pool",
    pool_size=5,
    **CONFIGURACAO,
)


def execute_query(sql, params=None, fetch=False):
    """Executa SELECT, UPDATE ou DELETE.

    fetch=True devolve uma lista de dicionarios.
    Sem fetch, confirma a alteracao e devolve a quantidade de linhas afetadas.
    """
    if params is None:
        params = ()

    conexao = pool.get_connection()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(sql, params)

        if fetch:
            resultado = cursor.fetchall()
        else:
            conexao.commit()
            resultado = cursor.rowcount

        return resultado
    except Error:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()


def execute_one(sql, params=None):
    """Devolve a primeira linha de um SELECT ou None."""
    linhas = execute_query(sql, params, fetch=True)
    return linhas[0] if linhas else None


def execute_insert(sql, params=None):
    """Executa INSERT e devolve o id gerado pelo AUTO_INCREMENT."""
    if params is None:
        params = ()

    conexao = pool.get_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute(sql, params)
        conexao.commit()
        return cursor.lastrowid
    except Error:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()
