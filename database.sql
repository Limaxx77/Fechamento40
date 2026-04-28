DROP TABLE IF EXISTS fechamentos;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fechamentos (
    id SERIAL PRIMARY KEY,

    usuario_id INTEGER REFERENCES usuarios(id),

    mes INTEGER NOT NULL,
    ano INTEGER NOT NULL,

    v_cred NUMERIC(10,2) DEFAULT 0,
    v_pix NUMERIC(10,2) DEFAULT 0,
    v_ifood NUMERIC(10,2) DEFAULT 0,
    v_din NUMERIC(10,2) DEFAULT 0,

    d_ifood NUMERIC(10,2) DEFAULT 0,
    d_stone NUMERIC(10,2) DEFAULT 0,

    dp_comp NUMERIC(10,2) DEFAULT 0,
    dp_bol NUMERIC(10,2) DEFAULT 0,
    dp_sal NUMERIC(10,2) DEFAULT 0,
    dp_pend NUMERIC(10,2) DEFAULT 0,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (mes, ano)
);
INSERT INTO usuarios (nome, usuario, senha_hash, role)
VALUES (
    'Administrador',
    '40graus',
    'COLE_AQUI_A_SENHA_HASH_GERADA',
    'admin'
);