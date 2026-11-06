"""Configuracao e conexao com o banco MySQL do projeto.

No XAMPP, o padrao costuma ser host=localhost, usuario=root,
senha vazia e porta=3306. Esses valores podem ser sobrescritos
por variaveis de ambiente.
"""

import os

import mysql.connector
from mysql.connector import Error


def get_connection():
    """Abre e retorna uma conexao com o banco projetorequerimento."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "projetorequerimento"),
        charset="utf8mb4",
        use_unicode=True,
    )


def testar_conexao():
    """Testa a conexao e retorna (sucesso, mensagem)."""
    conexao = None

    try:
        conexao = get_connection()
        if conexao.is_connected():
            return True, "Conexao com o MySQL realizada com sucesso."
        return False, "O MySQL nao confirmou a conexao."
    except Error as erro:
        return False, f"Erro ao conectar ao MySQL: {erro}"
    finally:
        if conexao is not None and conexao.is_connected():
            conexao.close()
