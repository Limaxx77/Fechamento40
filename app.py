import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def criar_tabelas():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            role VARCHAR(20) DEFAULT 'admin',
            ativo BOOLEAN DEFAULT TRUE,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fechamentos (
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
    """)

    conn.commit()
    cur.close()
    conn.close()


def criar_admin_padrao():
    conn = get_conn()
    cur = conn.cursor()

    usuario = "40graus"
    senha = "admin2024"
    senha_hash = generate_password_hash(senha)

    cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
    existe = cur.fetchone()

    if not existe:
        cur.execute("""
            INSERT INTO usuarios (nome, usuario, senha_hash, role)
            VALUES (%s, %s, %s, %s)
        """, ("Administrador", usuario, senha_hash, "admin"))

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "mensagem": "API 40 Graus funcionando"
    })


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    usuario = data.get("usuario")
    senha = data.get("senha")

    if not usuario or not senha:
        return jsonify({"status": "erro", "mensagem": "Usuário e senha são obrigatórios"}), 400

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id, nome, usuario, senha_hash, role, ativo
        FROM usuarios
        WHERE usuario = %s
    """, (usuario,))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return jsonify({"status": "erro", "mensagem": "Usuário não encontrado"}), 401

    if not user["ativo"]:
        return jsonify({"status": "erro", "mensagem": "Usuário inativo"}), 403

    if check_password_hash(user["senha_hash"], senha):
        return jsonify({
            "status": "ok",
            "user_id": user["id"],
            "nome": user["nome"],
            "usuario": user["usuario"],
            "role": user["role"]
        })

    return jsonify({"status": "erro", "mensagem": "Senha incorreta"}), 401


@app.route("/salvar", methods=["POST"])
def salvar_fechamento():
    data = request.get_json()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO fechamentos (
            usuario_id, mes, ano,
            v_cred, v_pix, v_ifood, v_din,
            d_ifood, d_stone,
            dp_comp, dp_bol, dp_sal, dp_pend,
            atualizado_em
        )
        VALUES (
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (mes, ano)
        DO UPDATE SET
            usuario_id = EXCLUDED.usuario_id,
            v_cred = EXCLUDED.v_cred,
            v_pix = EXCLUDED.v_pix,
            v_ifood = EXCLUDED.v_ifood,
            v_din = EXCLUDED.v_din,
            d_ifood = EXCLUDED.d_ifood,
            d_stone = EXCLUDED.d_stone,
            dp_comp = EXCLUDED.dp_comp,
            dp_bol = EXCLUDED.dp_bol,
            dp_sal = EXCLUDED.dp_sal,
            dp_pend = EXCLUDED.dp_pend,
            atualizado_em = CURRENT_TIMESTAMP
    """, (
        data.get("usuario_id"),
        data.get("mes"),
        data.get("ano"),

        data.get("v_cred", 0),
        data.get("v_pix", 0),
        data.get("v_ifood", 0),
        data.get("v_din", 0),

        data.get("d_ifood", 0),
        data.get("d_stone", 0),

        data.get("dp_comp", 0),
        data.get("dp_bol", 0),
        data.get("dp_sal", 0),
        data.get("dp_pend", 0)
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "salvo"})


@app.route("/fechamentos", methods=["GET"])
def listar_fechamentos():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT *
        FROM fechamentos
        ORDER BY ano DESC, mes DESC
    """)

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(dados)


@app.route("/fechamento/<int:ano>/<int:mes>", methods=["GET"])
def buscar_fechamento(ano, mes):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT *
        FROM fechamentos
        WHERE ano = %s AND mes = %s
    """, (ano, mes))

    dado = cur.fetchone()

    cur.close()
    conn.close()

    if dado:
        return jsonify(dado)

    return jsonify({})


@app.route("/deletar/<int:id>", methods=["DELETE"])
def deletar_fechamento(id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM fechamentos WHERE id = %s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "deletado"})


@app.route("/criar_usuario", methods=["POST"])
def criar_usuario():
    data = request.get_json()

    nome = data.get("nome")
    usuario = data.get("usuario")
    senha = data.get("senha")

    if not nome or not usuario or not senha:
        return jsonify({"status": "erro", "mensagem": "Preencha todos os campos"}), 400

    senha_hash = generate_password_hash(senha)

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO usuarios (nome, usuario, senha_hash, role)
            VALUES (%s, %s, %s, %s)
        """, (nome, usuario, senha_hash, "usuario"))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "criado"})

    except psycopg2.errors.UniqueViolation:
        return jsonify({"status": "erro", "mensagem": "Usuário já existe"}), 409


if DATABASE_URL:
    criar_tabelas()
    criar_admin_padrao()


if __name__ == "__main__":
    app.run(debug=True)