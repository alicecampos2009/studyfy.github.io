from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)

# Chave que o Flask usa para lembrar quem está logado (a "sessão").
# Pode trocar por qualquer frase sua e não mostre para ninguém.
app.secret_key = "studyfy-troque-esta-frase-por-uma-sua"

# O banco fica na mesma pasta do app.py (assim não importa de onde você rodar o projeto)
PASTA = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(PASTA, "studyfy.db")

# Quantos dias uma tarefa fica na lixeira antes de ser apagada de vez
DIAS_NA_LIXEIRA = 30

# ==========================================
# BANCO DE DADOS
# ==========================================

# Abre a conexão com o banco
def conectar():
    conexao = sqlite3.connect(BANCO)
    # Com isso dá para usar tarefa.nome no HTML
    conexao.row_factory = sqlite3.Row
    return conexao

# Cria as tabelas se ainda não existirem (é o mesmo que o banco.sql faz no DBeaver)
def criar_tabelas():
    conexao = conectar()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)
    # usuario_id = de quem é a tarefa
    # excluida_em = quando foi para a lixeira (vazio = tarefa normal, fora da lixeira)
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            urgente INTEGER NOT NULL DEFAULT 0,
            concluida INTEGER NOT NULL DEFAULT 0,
            usuario_id INTEGER,
            excluida_em TEXT
        )
    """)

    # Se o banco é da versão antiga, adiciona as colunas novas sem perder nada
    colunas = [coluna["name"] for coluna in conexao.execute("PRAGMA table_info(tarefas)")]
    if "usuario_id" not in colunas:
        conexao.execute("ALTER TABLE tarefas ADD COLUMN usuario_id INTEGER")
        # As tarefas que já existiam ficam com o primeiro usuário cadastrado
        conexao.execute("UPDATE tarefas SET usuario_id = (SELECT MIN(id) FROM usuarios)")
    if "excluida_em" not in colunas:
        conexao.execute("ALTER TABLE tarefas ADD COLUMN excluida_em TEXT")

    conexao.commit()
    conexao.close()

criar_tabelas()

# Apaga de vez as tarefas que já passaram 30 dias na lixeira
def esvaziar_lixeira(conexao):
    conexao.execute(
        "DELETE FROM tarefas WHERE excluida_em IS NOT NULL AND excluida_em < datetime('now', ?)",
        (f"-{DIAS_NA_LIXEIRA} days",)
    )
    conexao.commit()

# ==========================================
# LOGIN (quem está logado fica guardado na "session")
# ==========================================

# Coloque @precisa_login embaixo do @app.route das páginas que só quem entrou pode ver
def precisa_login(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return funcao(*args, **kwargs)
    return verificar

# Depois de concluir/excluir, volta para a página onde a pessoa estava
def voltar():
    if request.form.get("voltar") == "urgentes":
        return redirect(url_for("urgentes"))
    return redirect(url_for("listar"))

# Muda uma tarefa, mas só se ela for do usuário que está logado
def mudar_tarefa(comando, id):
    conexao = conectar()
    conexao.execute(comando, (id, session["usuario_id"]))
    conexao.commit()
    conexao.close()

# ==========================================
# ROTAS
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        # Procura no banco um usuário com esse nome e essa senha
        conexao = conectar()
        user = conexao.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND senha = ?",
            (usuario, senha)
        ).fetchone()
        conexao.close()

        if user:
            # Guarda quem entrou. Daqui para frente o site sabe de quem são as tarefas.
            session["usuario_id"] = user["id"]
            return redirect(url_for("menu"))

        erro = "Usuário ou senha incorretos!"

    return render_template("login.html", erro=erro)

# SAIR
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("index"))

# CRIAR CONTA
@app.route("/criarConta", methods=["GET", "POST"])
def criarConta():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        conexao = conectar()

        # Verifica se o usuario já existe
        ja_existe = conexao.execute(
            "SELECT id FROM usuarios WHERE usuario = ?",
            (usuario,)
        ).fetchone()

        if ja_existe:
            conexao.close()
            return render_template("criarConta.html", erro="Nome de usuário já existe!")

        # Salva o novo usuário
        conexao.execute(
            "INSERT INTO usuarios (nome, email, usuario, senha) VALUES (?, ?, ?, ?)",
            (nome, email, usuario, senha)
        )
        conexao.commit()
        conexao.close()

        return redirect(url_for("login"))

    return render_template("criarConta.html")

# MENU
@app.route("/menu")
@precisa_login
def menu():
    return render_template("menu.html")

# CADASTRAR TAREFA
@app.route("/nova_tarefa", methods=["GET", "POST"])
@precisa_login
def nova_tarefa():
    if request.method == "POST":
        nome = request.form.get("nome")
        urgente = request.form.get("urgente")

        # Se escolheu "s" (Sim) guarda 1, senão guarda 0
        if urgente == "s":
            urgente = 1
        else:
            urgente = 0

        # A tarefa nasce já com o dono: o usuário que está logado
        conexao = conectar()
        conexao.execute(
            "INSERT INTO tarefas (nome, urgente, concluida, usuario_id) VALUES (?, ?, 0, ?)",
            (nome, urgente, session["usuario_id"])
        )
        conexao.commit()
        conexao.close()

        return redirect(url_for("listar"))

    return render_template("nova_tarefa.html")

# LISTAR TAREFAS (só as do usuário logado e que não estão na lixeira)
@app.route("/listar")
@precisa_login
def listar():
    conexao = conectar()
    esvaziar_lixeira(conexao)
    tarefas = conexao.execute(
        "SELECT * FROM tarefas WHERE usuario_id = ? AND excluida_em IS NULL ORDER BY id",
        (session["usuario_id"],)
    ).fetchall()
    conexao.close()
    return render_template("listar.html", tarefas=tarefas)

# TAREFAS URGENTES
@app.route("/urgentes")
@precisa_login
def urgentes():
    conexao = conectar()
    esvaziar_lixeira(conexao)
    tarefas = conexao.execute(
        "SELECT * FROM tarefas WHERE usuario_id = ? AND urgente = 1 AND excluida_em IS NULL ORDER BY id",
        (session["usuario_id"],)
    ).fetchall()
    conexao.close()
    return render_template("urgentes.html", tarefas=tarefas)

# CONCLUIR TAREFA
@app.route("/concluir/<int:id>", methods=["POST"])
@precisa_login
def concluir(id):
    mudar_tarefa("UPDATE tarefas SET concluida = 1 WHERE id = ? AND usuario_id = ?", id)
    flash("Tarefa concluída! Foi sem querer? É só clicar em Desfazer.")
    return voltar()

# DESFAZER A CONCLUSÃO (a tarefa volta a ficar pendente)
@app.route("/desfazer/<int:id>", methods=["POST"])
@precisa_login
def desfazer(id):
    mudar_tarefa("UPDATE tarefas SET concluida = 0 WHERE id = ? AND usuario_id = ?", id)
    flash("Pronto, a tarefa voltou para a lista de pendentes.")
    return voltar()

# EXCLUIR TAREFA (não apaga de verdade: só manda para a lixeira)
@app.route("/excluir/<int:id>", methods=["POST"])
@precisa_login
def excluir(id):
    mudar_tarefa("UPDATE tarefas SET excluida_em = datetime('now') WHERE id = ? AND usuario_id = ?", id)
    flash(f"Tarefa enviada para a lixeira. Você pode restaurá-la em até {DIAS_NA_LIXEIRA} dias.")
    return voltar()

# LIXEIRA
@app.route("/lixeira")
@precisa_login
def lixeira():
    conexao = conectar()
    esvaziar_lixeira(conexao)
    # dias_restantes = quantos dias faltam para a tarefa ser apagada de vez
    tarefas = conexao.execute(
        """SELECT *, CAST(julianday(excluida_em, ?) - julianday('now') AS INTEGER) + 1 AS dias_restantes
           FROM tarefas
           WHERE usuario_id = ? AND excluida_em IS NOT NULL
           ORDER BY excluida_em DESC""",
        (f"+{DIAS_NA_LIXEIRA} days", session["usuario_id"])
    ).fetchall()
    conexao.close()
    return render_template("lixeira.html", tarefas=tarefas, dias=DIAS_NA_LIXEIRA)

# RESTAURAR TAREFA DA LIXEIRA
@app.route("/restaurar/<int:id>", methods=["POST"])
@precisa_login
def restaurar(id):
    mudar_tarefa("UPDATE tarefas SET excluida_em = NULL WHERE id = ? AND usuario_id = ?", id)
    flash("Tarefa restaurada! Ela já está de volta na sua lista.")
    return redirect(url_for("lixeira"))

if __name__ == "__main__":
    app.run(debug=True)
