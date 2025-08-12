import sqlite3

DB_FILE = 'clinica.db'

# --- Inicialização e Migração ---

def inicializar_banco_de_dados():
    """
    Cria as tabelas se não existirem e garante que o schema da tabela 'sessoes'
    esteja atualizado, adicionando colunas que faltam. Deve ser chamada no início do app.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # 1. Criar tabela de pacientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            data_nascimento TEXT NOT NULL, -- Armazenado como YYYY-MM-DD
            nome_responsavel TEXT NOT NULL
        )
        """)

        # 2. Criar tabela de sessões (se não existir)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            data_sessao TEXT NOT NULL, -- Armazenado como YYYY-MM-DD
            resumo_sessao TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
        )
        """)

        # 3. Migração de Schema para 'sessoes'
        cursor.execute("PRAGMA table_info(sessoes)")
        colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]

        colunas_necessarias = {
            "nivel_evolucao": "TEXT",
            "observacoes_evolucao": "TEXT",
            "plano_terapeutico": "TEXT"
        }

        for coluna, tipo in colunas_necessarias.items():
            if coluna not in colunas_existentes:
                print(f"Atualizando schema: Adicionando coluna '{coluna}' à tabela 'sessoes'...")
                cursor.execute(f"ALTER TABLE sessoes ADD COLUMN {coluna} {tipo}")
        
        print("Banco de dados pronto.")

# --- Funções de Pacientes ---

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
        conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_completo, data_nascimento, nome_responsavel FROM pacientes ORDER BY nome_completo")
        # Converte os objetos Row para dicionários para desacoplar do sqlite3
        return [dict(row) for row in cursor.fetchall()]

def buscar_paciente_por_id(paciente_id):
    """Busca um paciente específico pelo seu ID."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_completo, data_nascimento, nome_responsavel FROM pacientes WHERE id = ?", (paciente_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def atualizar_paciente(paciente_id, nome, data_nasc, responsavel):
    """Atualiza os dados de um paciente existente."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE pacientes
            SET nome_completo = ?, 
                data_nascimento = ?, 
                nome_responsavel = ?
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
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome_completo, data_nascimento, nome_responsavel FROM pacientes WHERE lower(nome_completo) LIKE ? ORDER BY nome_completo",
            ('%' + termo_busca.lower() + '%',)
        )
        return [dict(row) for row in cursor.fetchall()]

# --- Funções de Sessões ---

def adicionar_sessao(paciente_id, data, resumo, evolucao, obs_evolucao, plano):
    """Adiciona uma nova sessão para um paciente."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO sessoes (paciente_id, data_sessao, resumo_sessao, nivel_evolucao, 
                                  observacoes_evolucao, plano_terapeutico) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (paciente_id, data, resumo, evolucao, obs_evolucao, plano)
        )

def listar_sessoes_por_paciente(paciente_id):
    """Retorna uma lista de todas as sessões de um paciente, ordenadas pela data mais recente."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, data_sessao, nivel_evolucao, resumo_sessao FROM sessoes WHERE paciente_id = ? ORDER BY data_sessao DESC",
            (paciente_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def buscar_sessao_por_id(sessao_id):
    """Busca uma sessão específica com todos os seus detalhes pelo ID."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT data_sessao, resumo_sessao, nivel_evolucao, 
                      observacoes_evolucao, plano_terapeutico
               FROM sessoes WHERE id = ?""",
            (sessao_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def atualizar_sessao(sessao_id, data, resumo, evolucao, obs_evolucao, plano):
    """Atualiza os dados de uma sessão existente."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE sessoes SET data_sessao = ?, resumo_sessao = ?, nivel_evolucao = ?,
                                 observacoes_evolucao = ?, plano_terapeutico = ?
               WHERE id = ?""",
            (data, resumo, evolucao, obs_evolucao, plano, sessao_id)
        )

def excluir_sessao(sessao_id):
    """Exclui uma sessão do banco de dados."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessoes WHERE id = ?", (sessao_id,))