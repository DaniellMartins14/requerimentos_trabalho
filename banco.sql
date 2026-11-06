-- =========================================================
-- HD2R | CADASTRO DE MUNICIPES
-- Banco de dados do sistema de requerimentos municipais
-- Mantidas exatamente 3 tabelas:
--   1. municipes
--   2. processos
--   3. inscricoes_municipais
-- =========================================================

CREATE DATABASE IF NOT EXISTS projetorequerimento
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE projetorequerimento;

-- =========================================================
-- TABELA: municipes
-- Armazena os dados pessoais, endereco e acesso ao sistema.
-- O campo nivel_acesso substitui uma tabela separada de perfis,
-- mantendo o projeto com exatamente 3 tabelas.
-- =========================================================

CREATE TABLE IF NOT EXISTS municipes (
    id_municipe BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL COMMENT 'Armazena o HASH da senha, nunca a senha em texto puro',
    telefone VARCHAR(20),
    data_nascimento DATE,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    nivel_acesso VARCHAR(30) NOT NULL DEFAULT 'municipe',
    cep VARCHAR(9),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deletado_em DATETIME NULL COMMENT 'Soft delete: preenchido quando o registro for removido logicamente'
) ENGINE=InnoDB;

-- =========================================================
-- TABELA: processos
-- Cada processo pertence a um municipe.
-- =========================================================

CREATE TABLE IF NOT EXISTS processos (
    id_processo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    municipe_id BIGINT UNSIGNED NOT NULL,
    data_execucao DATE NOT NULL,
    solicitacao TEXT NOT NULL,
    local_execucao VARCHAR(255) NOT NULL,
    secretaria_destinada VARCHAR(150) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deletado_em DATETIME NULL COMMENT 'Soft delete: preenchido quando o registro for removido logicamente',

    CONSTRAINT fk_processos_municipes
        FOREIGN KEY (municipe_id)
        REFERENCES municipes(id_municipe)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- TABELA: inscricoes_municipais
-- Cada inscricao municipal pertence a um municipe.
-- =========================================================

CREATE TABLE IF NOT EXISTS inscricoes_municipais (
    id_inscricao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    municipe_id BIGINT UNSIGNED NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    codigo_atividade VARCHAR(30) NOT NULL,
    atividade_secundaria VARCHAR(30),
    nome_fantasia VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deletado_em DATETIME NULL COMMENT 'Soft delete: preenchido quando o registro for removido logicamente',

    CONSTRAINT fk_inscricoes_municipais_municipes
        FOREIGN KEY (municipe_id)
        REFERENCES municipes(id_municipe)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- OBSERVACOES:
-- 1. O sistema deve gravar em senha_hash somente senhas com hash.
-- 2. Para exclusao logica, atualizar deletado_em = NOW().
-- 3. Nas consultas de listagem, considerar apenas deletado_em IS NULL.
-- 4. Os niveis de acesso previstos sao: municipe, servidor e administrador.
-- =========================================================
