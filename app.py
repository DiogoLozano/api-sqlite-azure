import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, jsonify, request, g

app = Flask(__name__)

# No Azure App Service (Linux) apenas a pasta /home é persistente.
# Localmente, o banco fica na pasta do projeto.
DB_PATH = os.environ.get(
    "DB_PATH",
    "/home/data/app.db" if os.path.isdir("/home") and os.environ.get("WEBSITE_SITE_NAME")
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db"),
)


def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        get_db().execute(
            """
            CREATE TABLE IF NOT EXISTS tarefas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo     TEXT NOT NULL,
                descricao  TEXT,
                concluida  INTEGER NOT NULL DEFAULT 0,
                criado_em  TEXT NOT NULL
            )
            """
        )
        get_db().commit()


init_db()


def row_to_dict(row):
    d = dict(row)
    d["concluida"] = bool(d["concluida"])
    return d


@app.get("/")
def index():
    return jsonify(
        status="online",
        api="API de Tarefas (Flask + SQLite)",
        endpoints=["GET /tarefas", "GET /tarefas/<id>", "POST /tarefas",
                   "PUT /tarefas/<id>", "DELETE /tarefas/<id>"],
    )


@app.get("/tarefas")
def listar():
    rows = get_db().execute("SELECT * FROM tarefas ORDER BY id").fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.get("/tarefas/<int:tid>")
def obter(tid):
    row = get_db().execute("SELECT * FROM tarefas WHERE id = ?", (tid,)).fetchone()
    if row is None:
        return jsonify(erro="Tarefa não encontrada"), 404
    return jsonify(row_to_dict(row))


@app.post("/tarefas")
def criar():
    data = request.get_json(silent=True) or {}
    titulo = (data.get("titulo") or "").strip()
    if not titulo:
        return jsonify(erro="O campo 'titulo' é obrigatório"), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO tarefas (titulo, descricao, criado_em) VALUES (?, ?, ?)",
        (titulo, data.get("descricao"), datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    row = db.execute("SELECT * FROM tarefas WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(row_to_dict(row)), 201


@app.put("/tarefas/<int:tid>")
def atualizar(tid):
    db = get_db()
    row = db.execute("SELECT * FROM tarefas WHERE id = ?", (tid,)).fetchone()
    if row is None:
        return jsonify(erro="Tarefa não encontrada"), 404
    data = request.get_json(silent=True) or {}
    titulo = (data.get("titulo", row["titulo"]) or "").strip()
    if not titulo:
        return jsonify(erro="O campo 'titulo' não pode ser vazio"), 400
    db.execute(
        "UPDATE tarefas SET titulo = ?, descricao = ?, concluida = ? WHERE id = ?",
        (titulo, data.get("descricao", row["descricao"]),
         int(bool(data.get("concluida", row["concluida"]))), tid),
    )
    db.commit()
    row = db.execute("SELECT * FROM tarefas WHERE id = ?", (tid,)).fetchone()
    return jsonify(row_to_dict(row))


@app.delete("/tarefas/<int:tid>")
def remover(tid):
    db = get_db()
    cur = db.execute("DELETE FROM tarefas WHERE id = ?", (tid,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify(erro="Tarefa não encontrada"), 404
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
