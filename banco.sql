-- ==========================================
-- BANCO DE DADOS DO STUDYFY (SQLite)
-- Rode este script no DBeaver (Alt + X) conectado ao arquivo studyfy.db
-- ==========================================

-- Tabela dos usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome    TEXT NOT NULL,
    email   TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,   -- UNIQUE: não deixa repetir o nome de usuário
    senha   TEXT NOT NULL
);

-- Tabela das tarefas
-- urgente e concluida guardam 0 (não) ou 1 (sim), porque o SQLite não tem tipo "verdadeiro/falso"
-- usuario_id  = id do dono da tarefa (cada usuário só vê as suas)
-- excluida_em = data em que foi para a lixeira (vazio = tarefa normal). Depois de 30 dias é apagada de vez.
CREATE TABLE IF NOT EXISTS tarefas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    urgente     INTEGER NOT NULL DEFAULT 0,
    concluida   INTEGER NOT NULL DEFAULT 0,
    usuario_id  INTEGER,
    excluida_em TEXT
);

-- Dados de exemplo (rode o script só uma vez, senão eles ficam repetidos)
INSERT INTO usuarios (nome, email, usuario, senha)
VALUES ('Marina', 'marinaoligomes53@gmail.com', 'marina', '12345467689');

INSERT INTO tarefas (nome, urgente, concluida, usuario_id) VALUES ('Atividade de Matemática', 1, 0, 1);
INSERT INTO tarefas (nome, urgente, concluida, usuario_id) VALUES ('atividade ti', 0, 0, 1);
INSERT INTO tarefas (nome, urgente, concluida, usuario_id) VALUES ('Atividade de Matemática', 1, 0, 1);

-- ------------------------------------------
-- JÁ TEM UM BANCO DA VERSÃO ANTIGA?
-- Não precisa fazer nada: o app.py adiciona as colunas novas sozinho na primeira vez que rodar
-- (as tarefas antigas ficam com o primeiro usuário cadastrado).
-- Se preferir fazer na mão, rode as linhas abaixo (tire os dois traços do começo).
-- Neste caso NÃO rode os INSERTs de cima.
-- ------------------------------------------
-- ALTER TABLE tarefas ADD COLUMN usuario_id INTEGER;
-- ALTER TABLE tarefas ADD COLUMN excluida_em TEXT;
-- UPDATE tarefas SET usuario_id = (SELECT MIN(id) FROM usuarios);
