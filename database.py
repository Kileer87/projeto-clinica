import sqlite3

DB_FILE = 'clinica.db'

def criar_tabela_pacientes():
    """Cria a tabela 'pacientes' se ela não existir."""
    # O 'with' garante que a conexão será fechada automaticamente
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            nome_responsavel TEXT NOT NULL
        )
        """)
        # O commit é chamado automaticamente ao sair do bloco 'with' se houver alterações

def adicionar_paciente(nome, data_nasc, responsavel):
    """Adiciona um novo paciente ao banco de dados."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pacientes (nome_completo, data_nascimento, nome_responsavel) VALUES (?, ?, ?)",
            (nome, data_nasc, responsavel)
        )

def listar_pacientes():
    """Retorna uma lista de todos os pacientes cadastrados, ordenados por nome."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Selecionamos o ID para futuras operações (editar, excluir)
        cursor.execute("SELECT id, nome_completo, data_nascimento, nome_responsavel FROM pacientes ORDER BY nome_completo")
        return cursor.fetchall()

def buscar_paciente_por_id(paciente_id):
    """Busca um paciente específico pelo seu ID."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_completo, data_nascimento, nome_responsavel FROM pacientes WHERE id = ?", (paciente_id,))
        return cursor.fetchone() # Retorna uma única tupla ou None

def atualizar_paciente(paciente_id, nome, data_nasc, responsavel):
    """Atualiza os dados de um paciente existente."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE pacientes
            SET nome_completo = ?, data_nascimento = ?, nome_responsavel = ?
            WHERE id = ?
            """,
            (nome, data_nasc, responsavel, paciente_id)
        )

def excluir_paciente(paciente_id):
    """Exclui um paciente do banco de dados pelo seu ID."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))

def buscar_pacientes_por_nome(termo_busca):
    """Busca pacientes cujo nome completo contenha o termo de busca (case-insensitive)."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Usamos o operador LIKE com '%' para buscar em qualquer parte do nome
        # A função lower() torna a busca case-insensitive
        cursor.execute(
            "SELECT id, nome_completo, data_nascimento, nome_responsavel FROM pacientes WHERE lower(nome_completo) LIKE ? ORDER BY nome_completo",
            ('%' + termo_busca.lower() + '%',)
        )
        return cursor.fetchall()

def criar_tabela_sessoes():
    """Cria a tabela 'sessoes' se ela não existir, com chave estrangeira para pacientes."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Habilita o suporte a chaves estrangeiras para garantir a integridade dos dados
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            data_sessao TEXT NOT NULL,
            resumo_sessao TEXT,
            proxima_sessao_foco TEXT,
            nivel_evolucao TEXT,
            terapia_segunda TEXT,
            terapia_terca TEXT,
            terapia_quarta TEXT,
            terapia_quinta TEXT,
            terapia_sexta TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
        )
        """)

def adicionar_sessao(paciente_id, data, resumo, foco, evolucao, seg, ter, qua, qui, sex):
    """Adiciona uma nova sessão para um paciente."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO sessoes (paciente_id, data_sessao, resumo_sessao, proxima_sessao_foco, 
                                  nivel_evolucao, terapia_segunda, terapia_terca, terapia_quarta, 
                                  terapia_quinta, terapia_sexta) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (paciente_id, data, resumo, foco, evolucao, seg, ter, qua, qui, sex)
        )

def listar_sessoes_por_paciente(paciente_id):
    """Retorna uma lista de todas as sessões de um paciente, ordenadas pela data mais recente."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, data_sessao, nivel_evolucao, resumo_sessao FROM sessoes WHERE paciente_id = ? ORDER BY data_sessao DESC",
            (paciente_id,)
        )
        return cursor.fetchall()

def buscar_sessao_por_id(sessao_id):
    """Busca uma sessão específica com todos os seus detalhes pelo ID."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT data_sessao, resumo_sessao, proxima_sessao_foco, nivel_evolucao, 
                      terapia_segunda, terapia_terca, terapia_quarta, terapia_quinta, terapia_sexta 
               FROM sessoes WHERE id = ?""",
            (sessao_id,)
        )
        return cursor.fetchone()

def atualizar_sessao(sessao_id, data, resumo, foco, evolucao, seg, ter, qua, qui, sex):
    """Atualiza os dados de uma sessão existente."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE sessoes SET data_sessao = ?, resumo_sessao = ?, proxima_sessao_foco = ?,
                                 nivel_evolucao = ?, terapia_segunda = ?, terapia_terca = ?,
                                 terapia_quarta = ?, terapia_quinta = ?, terapia_sexta = ?
               WHERE id = ?""",
            (data, resumo, foco, evolucao, seg, ter, qua, qui, sex, sessao_id)
        )

def excluir_sessao(sessao_id):
    """Exclui uma sessão do banco de dados."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessoes WHERE id = ?", (sessao_id,))
