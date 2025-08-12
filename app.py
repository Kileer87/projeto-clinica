import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date, datetime
import sqlite3
import database  # Importa nosso módulo de banco de dados
import calendar # Módulo para trabalhar com calendários mensais
from tkcalendar import Calendar # Importa o calendário

# Variável global para armazenar os dados do usuário logado
USUARIO_LOGADO = None

# --- Constantes e Dicionários Auxiliares ---
DIAS_SEMANA_MAP = {
    "Segunda-feira": 0, "Terça-feira": 1, "Quarta-feira": 2,
    "Quinta-feira": 3, "Sexta-feira": 4, "Sábado": 5, "Domingo": 6
}
DIAS_SEMANA_LISTA = list(DIAS_SEMANA_MAP.keys())
DIAS_SEMANA_INV_MAP = {v: k for k, v in DIAS_SEMANA_MAP.items()}

# --- Funções Auxiliares ---

def formatar_data_para_db(data_str):
    """Converte data de DD/MM/YYYY para YYYY-MM-DD para salvar no DB."""
    if not data_str:
        return None
    try:
        # Converte para o formato do banco de dados, que permite ordenação correta
        return datetime.strptime(data_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return None # Retorna None se o formato da data for inválido

def formatar_data_para_exibicao(data_str):
    """Converte data de YYYY-MM-DD para DD/MM/YYYY para exibir na UI."""
    if not data_str:
        return ""
    try:
        # Converte de volta para o formato amigável para o usuário
        return datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        return data_str # Se já estiver em outro formato, retorna o original

def calcular_idade(data_nasc_db):
    """Calcula a idade a partir da data de nascimento no formato YYYY-MM-DD."""
    if not data_nasc_db:
        return ""
    try:
        nascimento = datetime.strptime(data_nasc_db, '%Y-%m-%d').date()
        hoje = date.today()
        # Calcula a idade de forma precisa
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return idade
    except (ValueError, TypeError):
        return "" # Retorna vazio se a data for inválida

def salvar_paciente(janela_cadastro, entry_nome, entry_data, entry_resp):
    """Coleta os dados dos campos de entrada e salva no banco de dados."""
    nome = entry_nome.get().strip()
    data_nasc_str = entry_data.get().strip()
    responsavel = entry_resp.get().strip()

    if not nome or not data_nasc_str or not responsavel:
        messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios!", parent=janela_cadastro)
        return

    data_nasc_db = formatar_data_para_db(data_nasc_str)
    if not data_nasc_db:
        messagebox.showerror("Erro de Validação", "Formato de data inválido. Use DD/MM/AAAA.", parent=janela_cadastro)
        return

    try:
        database.adicionar_paciente(nome, data_nasc_db, responsavel)
        messagebox.showinfo("Sucesso", f"Paciente {nome} cadastrado com sucesso!", parent=janela_cadastro)
        janela_cadastro.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar: {e}", parent=janela_cadastro)

def salvar_alteracoes_paciente(janela_edicao, entry_nome, entry_data, entry_resp, paciente_id):
    """Salva as alterações de um paciente existente."""
    nome = entry_nome.get().strip()
    data_nasc_str = entry_data.get().strip()
    responsavel = entry_resp.get().strip()

    if not nome or not data_nasc_str or not responsavel:
        messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios!", parent=janela_edicao)
        return

    data_nasc_db = formatar_data_para_db(data_nasc_str)
    if not data_nasc_db:
        messagebox.showerror("Erro de Validação", "Formato de data inválido. Use DD/MM/AAAA.", parent=janela_edicao)
        return

    try:
        database.atualizar_paciente(paciente_id, nome, data_nasc_db, responsavel)
        messagebox.showinfo("Sucesso", "Dados do paciente atualizados com sucesso!", parent=janela_edicao)
        janela_edicao.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao atualizar: {e}", parent=janela_edicao)

def salvar_nova_sessao(janela_form, paciente_id, widgets):
    """Salva uma nova sessão no banco de dados."""
    try:
        data_sessao_str = widgets['data'].get().strip()
        resumo = widgets['resumo'].get("1.0", "end-1c").strip()
        evolucao = widgets['evolucao'].get()
        obs_evolucao = widgets['obs_evolucao'].get("1.0", "end-1c").strip()
        plano = widgets['plano'].get("1.0", "end-1c").strip()

        if not data_sessao_str:
            messagebox.showerror("Erro de Validação", "O campo 'Data da Sessão' é obrigatório.", parent=janela_form)
            return

        data_sessao_db = formatar_data_para_db(data_sessao_str)
        if not data_sessao_db:
            messagebox.showerror("Erro de Validação", "Formato de data inválido. Use DD/MM/AAAA.", parent=janela_form)
            return

        database.adicionar_sessao(paciente_id, widgets['medico_id'], data_sessao_db, widgets['horario'], widgets['hora_fim'], resumo, evolucao, obs_evolucao, plano)
        messagebox.showinfo("Sucesso", "Nova sessão registrada com sucesso!", parent=janela_form)
        janela_form.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar a sessão: {e}", parent=janela_form)

def salvar_alteracoes_sessao(janela_form, sessao_id, widgets):
    """Salva as alterações de uma sessão existente."""
    try:
        data_sessao_str = widgets['data'].get().strip()
        resumo = widgets['resumo'].get("1.0", "end-1c").strip()
        evolucao = widgets['evolucao'].get()
        obs_evolucao = widgets['obs_evolucao'].get("1.0", "end-1c").strip()
        plano = widgets['plano'].get("1.0", "end-1c").strip()

        if not data_sessao_str:
            messagebox.showerror("Erro de Validação", "O campo 'Data da Sessão' é obrigatório.", parent=janela_form)
            return

        data_sessao_db = formatar_data_para_db(data_sessao_str)
        if not data_sessao_db:
            messagebox.showerror("Erro de Validação", "Formato de data inválido. Use DD/MM/AAAA.", parent=janela_form)
            return

        database.atualizar_sessao(sessao_id, widgets['medico_id'], data_sessao_db, widgets['horario'], widgets['hora_fim'], resumo, evolucao, obs_evolucao, plano)
        messagebox.showinfo("Sucesso", "Sessão atualizada com sucesso!", parent=janela_form)
        janela_form.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar a sessão: {e}", parent=janela_form)


# --- Funções de Salvar/CRUD de Médicos ---

def salvar_medico(janela_cadastro, entry_nome, entry_espec, entry_contato):
    """Coleta os dados dos campos de entrada e salva um novo médico."""
    nome = entry_nome.get().strip()
    especialidade = entry_espec.get().strip()
    contato = entry_contato.get().strip()

    if not nome:
        messagebox.showerror("Erro de Validação", "O campo 'Nome Completo' é obrigatório!", parent=janela_cadastro)
        return

    try:
        database.adicionar_medico(nome, especialidade, contato)
        messagebox.showinfo("Sucesso", f"Médico(a) {nome} cadastrado(a) com sucesso!", parent=janela_cadastro)
        janela_cadastro.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar: {e}", parent=janela_cadastro)

def salvar_alteracoes_medico(janela_edicao, entry_nome, entry_espec, entry_contato, medico_id):
    """Salva as alterações de um médico existente."""
    nome = entry_nome.get().strip()
    especialidade = entry_espec.get().strip()
    contato = entry_contato.get().strip()

    if not nome:
        messagebox.showerror("Erro de Validação", "O campo 'Nome Completo' é obrigatório!", parent=janela_edicao)
        return

    try:
        database.atualizar_medico(medico_id, nome, especialidade, contato)
        messagebox.showinfo("Sucesso", "Dados do médico atualizados com sucesso!", parent=janela_edicao)
        janela_edicao.destroy()
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao atualizar: {e}", parent=janela_edicao)

# --- Funções para Abrir Janelas de Médicos ---

def abrir_janela_cadastro_medico(janela_pai, callback_atualizar):
    """Abre uma nova janela para o cadastro de médicos."""
    janela_cadastro = tk.Toplevel(janela_pai)
    janela_cadastro.title("Cadastrar Novo Médico/Terapeuta")
    janela_cadastro.geometry("400x200")
    janela_cadastro.resizable(False, False)
    janela_cadastro.transient(janela_pai)
    janela_cadastro.grab_set()

    frame = tk.Frame(janela_cadastro, padx=20, pady=20)
    frame.pack(expand=True, fill='both')

    tk.Label(frame, text="Nome Completo:").grid(row=0, column=0, sticky="w", pady=5)
    entry_nome = tk.Entry(frame, width=40)
    entry_nome.grid(row=0, column=1, pady=5)
    entry_nome.focus_set()

    tk.Label(frame, text="Especialidade:").grid(row=1, column=0, sticky="w", pady=5)
    entry_espec = tk.Entry(frame, width=40)
    entry_espec.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="Contato (Telefone/Email):").grid(row=2, column=0, sticky="w", pady=5)
    entry_contato = tk.Entry(frame, width=40)
    entry_contato.grid(row=2, column=1, pady=5)

    btn_salvar = tk.Button(frame, text="Salvar Cadastro", command=lambda: salvar_medico(janela_cadastro, entry_nome, entry_espec, entry_contato))
    btn_salvar.grid(row=3, column=1, sticky="e", pady=15)
    
    janela_pai.wait_window(janela_cadastro)
    callback_atualizar()

def abrir_janela_edicao_medico(janela_pai, medico_id, callback_atualizar):
    medico_data = database.buscar_medico_por_id(medico_id)
    janela_edicao = tk.Toplevel(janela_pai)
    janela_edicao.title("Editar Médico/Terapeuta")
    janela_edicao.geometry("400x200")
    frame = tk.Frame(janela_edicao, padx=20, pady=20)
    frame.pack(expand=True, fill='both')

    tk.Label(frame, text="Nome Completo:").grid(row=0, column=0, sticky="w", pady=5)
    entry_nome = tk.Entry(frame, width=40); entry_nome.grid(row=0, column=1, pady=5); entry_nome.insert(0, medico_data['nome_completo'])
    tk.Label(frame, text="Especialidade:").grid(row=1, column=0, sticky="w", pady=5)
    entry_espec = tk.Entry(frame, width=40); entry_espec.grid(row=1, column=1, pady=5); entry_espec.insert(0, medico_data['especialidade'] or "")
    tk.Label(frame, text="Contato:").grid(row=2, column=0, sticky="w", pady=5)
    entry_contato = tk.Entry(frame, width=40); entry_contato.grid(row=2, column=1, pady=5); entry_contato.insert(0, medico_data['contato'] or "")
    btn_salvar = tk.Button(frame, text="Salvar Alterações", command=lambda: salvar_alteracoes_medico(janela_edicao, entry_nome, entry_espec, entry_contato, medico_id))
    btn_salvar.grid(row=3, column=1, sticky="e", pady=15)
    janela_pai.wait_window(janela_edicao)
    callback_atualizar()

def abrir_janela_disponibilidade(janela_pai, medico_id, medico_nome):
    """Abre uma janela com calendário para gerenciar a disponibilidade mensal de um médico."""
    janela_disp = tk.Toplevel(janela_pai)
    janela_disp.title(f"Agenda Mensal de {medico_nome}")
    janela_disp.geometry("900x550")
    janela_disp.transient(janela_pai)
    janela_disp.grab_set()

    # --- Frames Principais ---
    left_frame = ttk.Frame(janela_disp, padding=10)
    left_frame.pack(side='left', fill='y')
    right_frame = ttk.Frame(janela_disp, padding=10)
    right_frame.pack(side='right', fill='both', expand=True)

    # --- Calendário (Esquerda) ---
    hoje = date.today()
    cal = Calendar(left_frame, selectmode='day', year=hoje.year, month=hoje.month, day=hoje.day,
                   locale='pt_BR', date_pattern='dd/mm/y')
    cal.pack(pady=10)
    cal.tag_config('disponivel', background='lightgreen', foreground='black')

    # --- Detalhes do Dia (Direita) ---
    lbl_data_selecionada = ttk.Label(right_frame, text="Selecione um dia no calendário", font=("Helvetica", 12, "bold"))
    lbl_data_selecionada.pack(pady=(0, 10))

    # Tabela de horários
    tree_frame = ttk.Frame(right_frame)
    tree_frame.pack(fill='both', expand=True, pady=5)
    cols = ('ID', 'Início', 'Fim')
    tree_horarios = ttk.Treeview(tree_frame, columns=cols, show='headings')
    tree_horarios.heading('ID', text='ID'); tree_horarios.column('ID', width=0, stretch=tk.NO) # Oculto
    tree_horarios.heading('Início', text='Horário de Início'); tree_horarios.column('Início', anchor='center', width=100)
    tree_horarios.heading('Fim', text='Horário de Fim'); tree_horarios.column('Fim', anchor='center', width=100)
    tree_horarios.pack(side='left', fill='both', expand=True)
    scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree_horarios.yview)
    tree_horarios.configure(yscroll=scrollbar.set); scrollbar.pack(side='right', fill='y')

    # Frame para adicionar novo horário
    add_frame = ttk.LabelFrame(right_frame, text="Adicionar Novo Horário", padding=10)
    add_frame.pack(fill='x', pady=10)
    ttk.Label(add_frame, text="Início (HH:MM):").grid(row=0, column=0, padx=5, pady=5)
    entry_inicio = ttk.Entry(add_frame, width=10)
    entry_inicio.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(add_frame, text="Fim (HH:MM):").grid(row=0, column=2, padx=5, pady=5)
    entry_fim = ttk.Entry(add_frame, width=10)
    entry_fim.grid(row=0, column=3, padx=5, pady=5)

    def marcar_dias_disponiveis():
        """Pinta os dias com disponibilidade no calendário."""
        cal.calevent_remove('all')
        ano, mes = cal.get_displayed_month()
        datas_disponiveis = database.listar_datas_disponiveis_por_mes(medico_id, ano, mes)
        for data_str in datas_disponiveis:
            try:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
                cal.calevent_create(data_obj, 'Disponível', tags='disponivel')
            except ValueError:
                continue

    def atualizar_horarios_do_dia(event=None): # Adicionado event=None para ser usado como callback
        """Carrega e exibe os horários para o dia selecionado no calendário."""
        for i in tree_horarios.get_children(): tree_horarios.delete(i)
        data_selecionada = cal.get_date()
        lbl_data_selecionada.config(text=f"Horários para {data_selecionada}")
        data_db = formatar_data_para_db(data_selecionada)
        horarios = database.listar_disponibilidade_por_data(medico_id, data_db)
        for horario in horarios:
            tree_horarios.insert("", "end", values=(horario['id'], horario['hora_inicio'], horario['hora_fim']))

    def adicionar_horario():
        inicio, fim = entry_inicio.get().strip(), entry_fim.get().strip()
        data_selecionada_str = cal.get_date()
        data_db = formatar_data_para_db(data_selecionada_str)

        # Validações
        try:
            datetime.strptime(inicio, '%H:%M'); datetime.strptime(fim, '%H:%M')
        except ValueError:
            messagebox.showerror("Formato Inválido", "O formato do horário deve ser HH:MM.", parent=janela_disp); return
        if datetime.strptime(inicio, '%H:%M') >= datetime.strptime(fim, '%H:%M'):
            messagebox.showwarning("Lógica Inválida", "O horário de início deve ser anterior ao de fim.", parent=janela_disp); return

        try:
            database.adicionar_disponibilidade(medico_id, data_db, inicio, fim)
            entry_inicio.delete(0, 'end'); entry_fim.delete(0, 'end')
            atualizar_horarios_do_dia()
            marcar_dias_disponiveis() # Garante que o dia seja marcado
        except sqlite3.Error as e:
            messagebox.showerror("Erro de BD", f"Não foi possível adicionar o horário: {e}", parent=janela_disp)

    def excluir_horario_selecionado():
        selected_item = tree_horarios.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Selecione um horário para excluir.", parent=janela_disp); return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este horário?", parent=janela_disp):
            try:
                disponibilidade_id = tree_horarios.item(selected_item)['values'][0]
                database.excluir_disponibilidade(disponibilidade_id)
                atualizar_horarios_do_dia()
                marcar_dias_disponiveis() # Atualiza o calendário caso o dia fique sem horários
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Não foi possível excluir o horário: {e}", parent=janela_disp)

    # --- Botões e Eventos ---
    ttk.Button(add_frame, text="Adicionar", command=adicionar_horario).grid(row=0, column=4, padx=5)

    bottom_buttons_frame = ttk.Frame(right_frame)
    bottom_buttons_frame.pack(fill='x', side='bottom', pady=(10,0))
    ttk.Button(bottom_buttons_frame, text="Excluir Horário Selecionado", command=excluir_horario_selecionado).pack(side='left')
    ttk.Button(bottom_buttons_frame, text="Fechar", command=janela_disp.destroy).pack(side='right')

    # Bind de eventos do calendário
    cal.bind("<<CalendarSelected>>", atualizar_horarios_do_dia)
    cal.bind("<<CalendarMonthChanged>>", lambda e: marcar_dias_disponiveis())

    # Carregamento inicial
    marcar_dias_disponiveis()
    atualizar_horarios_do_dia()

# --- Funções para Abrir Janelas de Pacientes ---


def abrir_janela_cadastro(janela_principal):
    """Abre uma nova janela para o cadastro de pacientes."""
    janela_cadastro = tk.Toplevel(janela_principal)
    janela_cadastro.title("Cadastrar Novo Paciente")
    janela_cadastro.geometry("400x200")
    janela_cadastro.resizable(False, False)
    janela_cadastro.transient(janela_principal)
    janela_cadastro.grab_set()

    frame = tk.Frame(janela_cadastro, padx=20, pady=20)
    frame.pack(expand=True, fill='both')

    tk.Label(frame, text="Nome Completo:").grid(row=0, column=0, sticky="w", pady=5)
    entry_nome = tk.Entry(frame, width=40)
    entry_nome.grid(row=0, column=1, pady=5)
    entry_nome.focus_set() # Foco automático no primeiro campo

    tk.Label(frame, text="Data de Nascimento\n(DD/MM/AAAA):").grid(row=1, column=0, sticky="w", pady=5)
    entry_data = tk.Entry(frame, width=40)
    entry_data.grid(row=1, column=1, pady=5)

    tk.Label(frame, text="Nome do Responsável:").grid(row=2, column=0, sticky="w", pady=5)
    entry_resp = tk.Entry(frame, width=40)
    entry_resp.grid(row=2, column=1, pady=5)


    btn_salvar = tk.Button(
        frame,
        text="Salvar Cadastro",
        command=lambda: salvar_paciente(janela_cadastro, entry_nome, entry_data, entry_resp)
    )
    btn_salvar.grid(row=3, column=1, sticky="e", pady=15)

def abrir_janela_edicao(janela_pai, paciente_id, callback_atualizar):
    """Abre uma janela para editar os dados de um paciente."""
    paciente_data = database.buscar_paciente_por_id(paciente_id)
    if not paciente_data:
        messagebox.showerror("Erro", "Paciente não encontrado.", parent=janela_pai)
        return

    janela_edicao = tk.Toplevel(janela_pai)
    janela_edicao.title("Editar Paciente")
    janela_edicao.geometry("400x200")
    janela_edicao.resizable(False, False)
    janela_edicao.transient(janela_pai)
    janela_edicao.grab_set()

    frame = tk.Frame(janela_edicao, padx=20, pady=20)
    frame.pack(expand=True, fill='both')

    # Labels e Entradas preenchidas com os dados atuais
    tk.Label(frame, text="Nome Completo:").grid(row=0, column=0, sticky="w", pady=5)
    entry_nome = tk.Entry(frame, width=40)
    entry_nome.grid(row=0, column=1, pady=5)
    entry_nome.insert(0, paciente_data['nome_completo'])
    entry_nome.focus_set() # Foco automático

    tk.Label(frame, text="Data de Nascimento\n(DD/MM/AAAA):").grid(row=1, column=0, sticky="w", pady=5)
    entry_data = tk.Entry(frame, width=40)
    entry_data.grid(row=1, column=1, pady=5)
    entry_data.insert(0, formatar_data_para_exibicao(paciente_data['data_nascimento']))

    tk.Label(frame, text="Nome do Responsável:").grid(row=2, column=0, sticky="w", pady=5)
    entry_resp = tk.Entry(frame, width=40)
    entry_resp.grid(row=2, column=1, pady=5)
    entry_resp.insert(0, paciente_data['nome_responsavel'])

    # Botão Salvar
    btn_salvar = tk.Button(
        frame,
        text="Salvar Alterações",
        command=lambda: salvar_alteracoes_paciente(janela_edicao, entry_nome, entry_data, entry_resp, paciente_id)
    )
    btn_salvar.grid(row=3, column=1, sticky="e", pady=15)

    # Espera a janela de edição ser fechada e depois chama o callback para atualizar a lista.
    janela_pai.wait_window(janela_edicao)
    callback_atualizar()

def criar_abas_sessao(frame_pai):
    """Cria e retorna um notebook com abas para o formulário de sessão."""
    notebook = ttk.Notebook(frame_pai)
    notebook.pack(expand=True, fill='both', pady=5)

    # Aba 1: Avaliação da Sessão
    aba1 = ttk.Frame(notebook, padding=10)
    notebook.add(aba1, text=' Avaliação da Sessão ')

    # Aba 2: Plano Terapêutico
    aba2 = ttk.Frame(notebook, padding=10)
    notebook.add(aba2, text=' Plano Terapêutico ')

    # --- Widgets da Aba 1 ---
    frame_evolucao = ttk.Frame(aba1)
    frame_evolucao.pack(fill='x', pady=(0, 10))
    ttk.Label(frame_evolucao, text="Nível de Evolução:").pack(side='left')
    combo_evolucao = ttk.Combobox(frame_evolucao, values=["Iniciante", "Intermediário", "Avançado", "Manutenção"])
    combo_evolucao.pack(side='left', padx=5)

    ttk.Label(aba1, text="Resumo da Sessão (o que foi trabalhado):").pack(anchor='w', pady=(5,0))
    text_resumo = tk.Text(aba1, width=50, height=8, wrap='word')
    text_resumo.pack(expand=True, fill='both', pady=(0, 10))

    ttk.Label(aba1, text="Observações sobre a Evolução do Paciente:").pack(anchor='w')
    text_obs_evolucao = tk.Text(aba1, width=50, height=8, wrap='word')
    text_obs_evolucao.pack(expand=True, fill='both')

    # --- Widgets da Aba 2 ---
    ttk.Label(aba2, text="Plano Terapêutico (atividades, metas e estratégias para as próximas sessões):").pack(anchor='w')
    text_plano = tk.Text(aba2, width=50, height=15, wrap='word')
    text_plano.pack(expand=True, fill='both', pady=5)

    return {
        "resumo": text_resumo, "evolucao": combo_evolucao, 
        "obs_evolucao": text_obs_evolucao, "plano": text_plano
    }

def abrir_janela_detalhes_sessao(janela_pai, sessao_id):
    """Abre uma janela para exibir os detalhes completos de uma sessão."""
    sessao_data = database.buscar_sessao_por_id(sessao_id)
    if not sessao_data:
        messagebox.showerror("Erro", "Sessão não encontrada.", parent=janela_pai)
        return
    
    janela_detalhes = tk.Toplevel(janela_pai)
    data_exibicao = formatar_data_para_exibicao(sessao_data['data_sessao'])
    janela_detalhes.title(f"Detalhes da Sessão - {data_exibicao if data_exibicao else 'Data Inválida'}")
    janela_detalhes.geometry("600x500")
    janela_detalhes.resizable(False, False)
    janela_detalhes.transient(janela_pai)
    janela_detalhes.grab_set()

    frame = ttk.Frame(janela_detalhes, padding="15")
    frame.pack(expand=True, fill='both')
    
    widgets = criar_abas_sessao(frame)
    
    # Preenche os dados e desabilita a edição
    widgets['resumo'].insert('1.0', sessao_data['resumo_sessao'] or "")
    widgets['evolucao'].set(sessao_data['nivel_evolucao'] or "")
    widgets['obs_evolucao'].insert('1.0', sessao_data['observacoes_evolucao'] or "")
    widgets['plano'].insert('1.0', sessao_data['plano_terapeutico'] or "")

    for w in widgets.values():
        if isinstance(w, (tk.Text, ttk.Entry, ttk.Combobox)):
            w.config(state='disabled')

    ttk.Button(frame, text="Fechar", command=janela_detalhes.destroy).pack(side='bottom', pady=(10, 0))

def abrir_janela_sessoes(janela_pai, paciente_id, paciente_nome, callback_atualizar_calendario):
    """Abre uma janela para listar e gerenciar as sessões de um paciente."""
    janela_sessoes = tk.Toplevel(janela_pai)
    janela_sessoes.title(f"Sessões de {paciente_nome}")
    janela_sessoes.geometry("800x500")
    janela_sessoes.transient(janela_pai)
    janela_sessoes.grab_set()
    # Garante que o calendário seja atualizado se a janela for fechada
    janela_sessoes.bind("<Destroy>", lambda e: callback_atualizar_calendario() if e.widget == janela_sessoes else None)

    frame = ttk.Frame(janela_sessoes, padding="10")
    frame.pack(expand=True, fill='both')

    # Tabela de Sessões
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(expand=True, fill='both')
    cols = ('ID', 'Data', 'Horário', 'Médico/Terapeuta', 'Nível de Evolução', 'Resumo')
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings')

    tree.heading('ID', text='ID')
    tree.column('ID', width=50, anchor='center')
    tree.heading('Data', text='Data')
    tree.column('Data', width=100, anchor='center')
    tree.heading('Horário', text='Horário')
    tree.column('Horário', width=80, anchor='center')
    tree.heading('Médico/Terapeuta', text='Médico/Terapeuta')
    tree.column('Médico/Terapeuta', width=180)
    tree.heading('Nível de Evolução', text='Nível de Evolução')
    tree.column('Nível de Evolução', width=120, anchor='center')
    tree.heading('Resumo', text='Resumo da Sessão')
    tree.column('Resumo', width=250)

    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    def recarregar_sessoes():
        for i in tree.get_children():
            tree.delete(i)
        try:
            for sessao in database.listar_sessoes_por_paciente(paciente_id):
                # sessao = {'id': ..., 'data_sessao': ..., 'nivel_evolucao': ..., 'resumo_sessao': ...}
                # Limita o resumo para exibição na tabela e remove quebras de linha
                data_exibicao = formatar_data_para_exibicao(sessao['data_sessao'])
                resumo_original = sessao['resumo_sessao'] or ""
                resumo_curto = (resumo_original[:75] + '...') if len(resumo_original) > 75 else resumo_original
                tree.insert("", "end", values=(sessao['id'], data_exibicao, sessao['hora_inicio_sessao'] or '', sessao['medico_nome'] or 'Não definido', sessao['nivel_evolucao'], resumo_curto.replace('\n', ' ')))
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar sessões: {e}", parent=janela_sessoes)

    def callback_combinado():
        """Função que atualiza tanto a lista de sessões quanto o calendário principal."""
        recarregar_sessoes()
        if callback_atualizar_calendario:
            callback_atualizar_calendario()

    def ao_clicar_duas_vezes(event):
        """Abre os detalhes da sessão ao dar um duplo clique."""
        item_selecionado = tree.focus()
        if item_selecionado:
            sessao_id = tree.item(item_selecionado)['values'][0]
            abrir_janela_detalhes_sessao(janela_sessoes, sessao_id)

    tree.bind("<Double-1>", ao_clicar_duas_vezes)

    # Botões de Ação
    botoes_frame = ttk.Frame(frame)
    botoes_frame.pack(fill='x', side='bottom', pady=(10, 0))
    
    btn_adicionar = ttk.Button(
        botoes_frame, 
        text="Adicionar Nova Sessão", 
        command=lambda: abrir_janela_form_sessao(janela_sessoes, callback_combinado, paciente_id=paciente_id)
    )
    btn_adicionar.pack(side='left', padx=5)
    
    def editar_sessao_selecionada():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma sessão para editar.", parent=janela_sessoes)
            return
        sessao_id = tree.item(selected_item)['values'][0]
        abrir_janela_edicao_sessao(janela_sessoes, sessao_id, callback_combinado)

    def excluir_sessao_selecionada():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma sessão para excluir.", parent=janela_sessoes)
            return
        
        sessao_id = tree.item(selected_item)['values'][0]
        confirmar = messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir esta sessão?", parent=janela_sessoes)
        if confirmar:
            try:
                database.excluir_sessao(sessao_id)
                messagebox.showinfo("Sucesso", "Sessão excluída com sucesso.", parent=janela_sessoes)
                callback_combinado() # Atualiza lista e calendário
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir sessão: {e}", parent=janela_sessoes)

    ttk.Button(botoes_frame, text="Editar Sessão", command=editar_sessao_selecionada).pack(side='left', padx=5)
    ttk.Button(botoes_frame, text="Excluir Sessão", command=excluir_sessao_selecionada).pack(side='left', padx=5)

    # Carrega os dados iniciais
    recarregar_sessoes()

def abrir_janela_form_sessao(janela_pai, callback_atualizar, paciente_id=None, sessao_id=None):
    """Abre um formulário para adicionar uma nova sessão."""
    janela_form = tk.Toplevel(janela_pai)
    janela_form.title("Registrar Nova Sessão" if not sessao_id else "Editar Sessão")
    janela_form.geometry("600x500")
    janela_form.resizable(False, False)
    janela_form.transient(janela_pai)
    janela_form.grab_set()

    frame = ttk.Frame(janela_form, padding="15")
    frame.pack(expand=True, fill='both')
    
    frame_data = ttk.Frame(frame)
    frame_data.pack(fill='x')
    ttk.Label(frame_data, text="Data da Sessão\n(DD/MM/AAAA):").pack(side='left')
    entry_data = ttk.Entry(frame_data, width=20)
    entry_data.pack(side='left', padx=5)
    entry_data.focus_set()
    
    widgets = criar_abas_sessao(frame)
    widgets['data'] = entry_data # Adiciona a entrada de data ao dicionário

    if sessao_id: # Modo de edição
        sessao_data = database.buscar_sessao_por_id(sessao_id)
        entry_data.insert(0, formatar_data_para_exibicao(sessao_data['data_sessao']))
        widgets['resumo'].insert('1.0', sessao_data['resumo_sessao'] or "")
        widgets['evolucao'].set(sessao_data['nivel_evolucao'] or "")
        widgets['obs_evolucao'].insert('1.0', sessao_data['observacoes_evolucao'] or "")
        widgets['plano'].insert('1.0', sessao_data['plano_terapeutico'] or "")
    else: # Modo de criação
        entry_data.insert(0, date.today().strftime('%d/%m/%Y'))

    # Botão Salvar
    comando_salvar = lambda: (salvar_alteracoes_sessao(janela_form, sessao_id, widgets) if sessao_id 
                               else salvar_nova_sessao(janela_form, paciente_id, widgets))
    btn_salvar = ttk.Button(
        frame,
        text="Salvar Alterações" if sessao_id else "Salvar Sessão",
        command=comando_salvar
    )
    btn_salvar.pack(side='bottom', pady=(10, 0))

    # Atualiza a lista de sessões quando a janela de formulário é fechada
    janela_pai.wait_window(janela_form)
    callback_atualizar()

def abrir_janela_edicao_sessao(janela_pai, sessao_id, callback_atualizar):
    """Abre o formulário de sessão no modo de edição."""
    # Para editar, não precisamos do paciente_id inicialmente, pois já temos o sessao_id.
    # A função de salvar alterações usará o sessao_id.
    abrir_janela_form_sessao(janela_pai, callback_atualizar=callback_atualizar, sessao_id=sessao_id)

def abrir_janela_prontuario(janela_pai, paciente_id, paciente_nome):
    """Abre a janela do prontuário do paciente com abas para diferentes seções."""
    janela_prontuario = tk.Toplevel(janela_pai)
    janela_prontuario.title(f"Prontuário de {paciente_nome}")
    janela_prontuario.geometry("800x600")
    janela_prontuario.transient(janela_pai)
    janela_prontuario.grab_set()

    # --- Carrega os dados do prontuário ---
    try:
        prontuario_data = database.buscar_ou_criar_prontuario(paciente_id)
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Banco de Dados", f"Não foi possível carregar o prontuário: {e}", parent=janela_prontuario)
        janela_prontuario.destroy()
        return

    prontuario_id = prontuario_data['id']

    # --- Estrutura da Janela ---
    main_frame = ttk.Frame(janela_prontuario, padding=10)
    main_frame.pack(fill='both', expand=True)

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill='both', expand=True, pady=5)

    # --- Aba 1: Informações Gerais ---
    aba_info = ttk.Frame(notebook, padding=10)
    notebook.add(aba_info, text=' Informações Gerais ')

    ttk.Label(aba_info, text="Queixa Principal / Motivo da Consulta:", font=("Helvetica", 10, "bold")).pack(anchor='w')
    txt_queixa = tk.Text(aba_info, height=4, wrap='word'); txt_queixa.pack(fill='x', pady=(0, 10))
    txt_queixa.insert('1.0', prontuario_data.get('queixa_principal') or "")

    ttk.Label(aba_info, text="Histórico Médico Relevante (diagnósticos, alergias, etc.):", font=("Helvetica", 10, "bold")).pack(anchor='w')
    txt_historico = tk.Text(aba_info, height=6, wrap='word'); txt_historico.pack(fill='x', pady=(0, 10))
    txt_historico.insert('1.0', prontuario_data.get('historico_medico_relevante') or "")
    
    ttk.Label(aba_info, text="Informações Adicionais (contato de emergência, observações):", font=("Helvetica", 10, "bold")).pack(anchor='w')
    txt_info_adicional = tk.Text(aba_info, height=4, wrap='word'); txt_info_adicional.pack(fill='x', pady=(0, 10))
    txt_info_adicional.insert('1.0', prontuario_data.get('informacoes_adicionais') or "")

    # --- Aba 2: Anamnese ---
    aba_anamnese = ttk.Frame(notebook, padding=10)
    notebook.add(aba_anamnese, text=' Anamnese ')
    
    ttk.Label(aba_anamnese, text="Anamnese (histórico detalhado do desenvolvimento, familiar, social, etc.):", font=("Helvetica", 10, "bold")).pack(anchor='w')
    txt_anamnese = tk.Text(aba_anamnese, wrap='word'); txt_anamnese.pack(fill='both', expand=True, pady=5)
    txt_anamnese.insert('1.0', prontuario_data.get('anamnese') or "")

    # --- Botão Salvar ---
    def salvar_prontuario():
        try:
            database.atualizar_prontuario(prontuario_id, txt_queixa.get("1.0", "end-1c").strip(), txt_historico.get("1.0", "end-1c").strip(), txt_anamnese.get("1.0", "end-1c").strip(), txt_info_adicional.get("1.0", "end-1c").strip())
            messagebox.showinfo("Sucesso", "Prontuário salvo com sucesso!", parent=janela_prontuario)
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível salvar o prontuário: {e}", parent=janela_prontuario)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill='x', pady=(10, 0))
    ttk.Button(btn_frame, text="Salvar Prontuário", command=salvar_prontuario).pack(side='right')
    ttk.Button(btn_frame, text="Fechar", command=janela_prontuario.destroy).pack(side='right', padx=10)

def abrir_janela_lista_medicos(janela_principal):
    """Abre uma janela para listar e gerenciar todos os médicos."""
    janela_lista = tk.Toplevel(janela_principal)
    janela_lista.title("Médicos e Terapeutas Cadastrados")
    janela_lista.geometry("800x400")
    janela_lista.transient(janela_principal)
    janela_lista.grab_set()

    frame = ttk.Frame(janela_lista, padding="10")
    frame.pack(expand=True, fill='both')

    tree_frame = ttk.Frame(frame)
    tree_frame.pack(expand=True, fill='both', pady=(0, 10))
    cols = ('ID', 'Nome Completo', 'Especialidade', 'Contato')
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)

    tree.heading('ID', text='ID'); tree.column('ID', width=50, anchor='center')
    tree.heading('Nome Completo', text='Nome Completo'); tree.column('Nome Completo', width=300)
    tree.heading('Especialidade', text='Especialidade'); tree.column('Especialidade', width=200)
    tree.heading('Contato', text='Contato'); tree.column('Contato', width=200)
    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')
    tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)

    def recarregar_lista():
        for i in tree.get_children(): tree.delete(i)
        try:
            for medico in database.listar_medicos():
                tree.insert("", "end", values=(medico['id'], medico['nome_completo'], medico['especialidade'], medico['contato']))
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar médicos: {e}", parent=janela_lista)

    def editar_selecionado():
        selected_item = tree.focus()
        if not selected_item: return
        medico_id = tree.item(selected_item)['values'][0]
        abrir_janela_edicao_medico(janela_lista, medico_id, recarregar_lista)

    def gerenciar_disponibilidade():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um médico.", parent=janela_lista)
            return
        medico_id = tree.item(selected_item)['values'][0]
        medico_nome = tree.item(selected_item)['values'][1]
        abrir_janela_disponibilidade(janela_lista, medico_id, medico_nome)

    def excluir_selecionado():
        selected_item = tree.focus()
        if not selected_item: return
        medico_id = tree.item(selected_item)['values'][0]
        nome_medico = tree.item(selected_item)['values'][1]
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir '{nome_medico}'?", parent=janela_lista):
            try:
                database.excluir_medico(medico_id)
                recarregar_lista()
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}", parent=janela_lista)

    botoes_frame = ttk.Frame(frame)
    botoes_frame.pack(fill='x', side='bottom')
    ttk.Button(botoes_frame, text="Adicionar Novo", command=lambda: abrir_janela_cadastro_medico(janela_lista, recarregar_lista)).pack(side='left', padx=5)
    ttk.Button(botoes_frame, text="Editar Selecionado", command=editar_selecionado).pack(side='left', padx=5)
    ttk.Button(botoes_frame, text="Gerenciar Disponibilidade", command=gerenciar_disponibilidade).pack(side='left', padx=5)
    ttk.Button(botoes_frame, text="Excluir Selecionado", command=excluir_selecionado).pack(side='left', padx=5)

    recarregar_lista()


def abrir_janela_lista(janela_principal, callback_atualizar_calendario):
    """Abre uma janela para listar todos os pacientes."""
    janela_lista = tk.Toplevel(janela_principal)
    janela_lista.title("Lista de Pacientes Cadastrados")
    # Aumenta a largura para a nova coluna 'Idade'
    janela_lista.geometry("900x450")
    janela_lista.transient(janela_principal)
    janela_lista.grab_set()

    frame = ttk.Frame(janela_lista, padding="10")
    frame.pack(expand=True, fill='both')

    # --- Frame de Busca ---
    busca_frame = ttk.Frame(frame)
    busca_frame.pack(fill='x', pady=(0, 10))

    ttk.Label(busca_frame, text="Buscar por Nome:").pack(side='left', padx=(0, 5))
    entry_busca = ttk.Entry(busca_frame, width=40)
    entry_busca.pack(side='left', expand=True, fill='x', padx=5)

    def executar_busca():
        """Chama a função de recarregar lista com o termo da busca."""
        recarregar_lista(entry_busca.get())

    # Adiciona o evento <Return> (Enter) para o campo de busca
    entry_busca.bind("<Return>", lambda event: executar_busca())

    ttk.Button(busca_frame, text="Buscar", command=executar_busca).pack(side='left', padx=5)

    # --- Tabela (Treeview) ---
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(expand=True, fill='both')
    cols = ('ID', 'Nome Completo', 'Idade', 'Data de Nascimento', 'Responsável') # Colunas visíveis
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)

    # Configura os cabeçalhos e larguras das colunas
    tree.heading('ID', text='ID')
    tree.column('ID', width=50, anchor='center')
    tree.heading('Nome Completo', text='Nome Completo')
    tree.column('Nome Completo', width=280)
    tree.heading('Idade', text='Idade')
    tree.column('Idade', width=60, anchor='center')
    tree.heading('Data de Nascimento', text='Data de Nascimento')
    tree.column('Data de Nascimento', width=150, anchor='center')
    tree.heading('Responsável', text='Responsável')
    tree.column('Responsável', width=280)

    tree.grid(row=0, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # --- Funções de Ação da Janela de Lista ---
    def recarregar_lista(termo_busca=None):
        """Limpa a tabela e a recarrega com dados do banco."""
        # Limpa a visualização atual da árvore
        for i in tree.get_children():
            tree.delete(i)
        # Busca e insere os dados atualizados
        try:
            # Se um termo de busca foi fornecido (e não está vazio), busca por ele.
            if termo_busca and termo_busca.strip():
                pacientes = database.buscar_pacientes_por_nome(termo_busca)
            else: # Caso contrário, lista todos os pacientes.
                pacientes = database.listar_pacientes()

            for paciente in pacientes:
                idade = calcular_idade(paciente['data_nascimento'])
                data_nasc_exibicao = formatar_data_para_exibicao(paciente['data_nascimento'])
                # Monta a tupla na ordem correta das colunas da Treeview
                valores_para_inserir = (paciente['id'], paciente['nome_completo'], idade, data_nasc_exibicao, paciente['nome_responsavel'])
                tree.insert("", "end", values=valores_para_inserir)

        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao buscar pacientes: {e}", parent=janela_lista)

    def editar_selecionado():
        """Abre a janela de edição para o item selecionado."""
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um paciente para editar.", parent=janela_lista)
            return
        
        paciente_id = tree.item(selected_item)['values'][0]
        # Passa a função de recarregar como callback
        abrir_janela_edicao(janela_lista, paciente_id, recarregar_lista)

    def ver_sessoes_selecionado():
        """Abre a janela de sessões para o paciente selecionado."""
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um paciente para ver as sessões.", parent=janela_lista)
            return
        
        paciente_values = tree.item(selected_item)['values']
        paciente_id = paciente_values[0]
        paciente_nome = paciente_values[1]
        abrir_janela_sessoes(janela_lista, paciente_id, paciente_nome, callback_atualizar_calendario)

    def ver_prontuario_selecionado():
        """Abre a janela de prontuário para o paciente selecionado."""
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um paciente para ver o prontuário.", parent=janela_lista)
            return
        
        paciente_values = tree.item(selected_item)['values']
        paciente_id = paciente_values[0]
        paciente_nome = paciente_values[1]
        abrir_janela_prontuario(janela_lista, paciente_id, paciente_nome)

    def excluir_selecionado():
        """Exclui o item selecionado após confirmação."""
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione um paciente para excluir.", parent=janela_lista)
            return

        paciente_values = tree.item(selected_item)['values']
        paciente_id = paciente_values[0]
        paciente_nome = paciente_values[1]

        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o paciente '{paciente_nome}'?", parent=janela_lista)
        if confirmar:
            try:
                database.excluir_paciente(paciente_id)
                messagebox.showinfo("Sucesso", "Paciente excluído com sucesso.", parent=janela_lista)
                recarregar_lista() # Atualiza a lista após a exclusão
            except sqlite3.Error as e:
                messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao excluir: {e}", parent=janela_lista)

    def limpar_busca():
        """Limpa o campo de busca e recarrega a lista completa."""
        entry_busca.delete(0, 'end')
        recarregar_lista()

    ttk.Button(busca_frame, text="Limpar", command=limpar_busca).pack(side='left', padx=5)

    # --- Botões de Ação ---
    botoes_frame = ttk.Frame(frame)
    botoes_frame.pack(fill='x', side='bottom', pady=(10, 0))
    
    ttk.Button(botoes_frame, text="Editar Paciente", command=editar_selecionado).pack(side='left', padx=5)
    ttk.Button(botoes_frame, text="Excluir Paciente", command=excluir_selecionado).pack(side='left', padx=5)
    # Botões da direita são empilhados da direita para a esquerda
    ttk.Button(botoes_frame, text="Ver Sessões", command=ver_sessoes_selecionado).pack(side='right', padx=5)
    ttk.Button(botoes_frame, text="Ver Prontuário", command=ver_prontuario_selecionado).pack(side='right', padx=5)

    # Carrega os dados iniciais na tabela
    recarregar_lista()

# --- Funções de Gerenciamento de Usuários (Admin) ---

def abrir_janela_cadastro_usuario(janela_pai, callback_atualizar):
    """Abre uma janela para cadastrar um novo usuário."""
    janela_cad_user = tk.Toplevel(janela_pai)
    janela_cad_user.title("Cadastrar Novo Usuário")
    janela_cad_user.geometry("400x250")
    janela_cad_user.transient(janela_pai)
    janela_cad_user.grab_set()

    frame = ttk.Frame(janela_cad_user, padding=20)
    frame.pack(fill='both', expand=True)

    ttk.Label(frame, text="Nome de Usuário:").grid(row=0, column=0, sticky='w', pady=2)
    entry_user = ttk.Entry(frame, width=30)
    entry_user.grid(row=1, column=0, sticky='ew', pady=(0, 10))
    entry_user.focus_set()

    ttk.Label(frame, text="Senha:").grid(row=2, column=0, sticky='w', pady=2)
    entry_pass = ttk.Entry(frame, width=30, show="*")
    entry_pass.grid(row=3, column=0, sticky='ew', pady=(0, 10))

    ttk.Label(frame, text="Confirmar Senha:").grid(row=4, column=0, sticky='w', pady=2)
    entry_pass_confirm = ttk.Entry(frame, width=30, show="*")
    entry_pass_confirm.grid(row=5, column=0, sticky='ew', pady=(0, 10))

    ttk.Label(frame, text="Nível de Acesso:").grid(row=6, column=0, sticky='w', pady=2)
    combo_nivel = ttk.Combobox(frame, values=['terapeuta', 'admin'], state='readonly')
    combo_nivel.grid(row=7, column=0, sticky='ew')
    combo_nivel.set('terapeuta')

    def salvar_novo_usuario():
        user, p1, p2, nivel = entry_user.get().strip(), entry_pass.get(), entry_pass_confirm.get(), combo_nivel.get()
        if not (user and p1 and p2 and nivel):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.", parent=janela_cad_user); return
        if p1 != p2:
            messagebox.showerror("Erro", "As senhas não coincidem.", parent=janela_cad_user); return
        if len(p1) < 6:
            messagebox.showwarning("Senha Fraca", "A senha deve ter no mínimo 6 caracteres.", parent=janela_cad_user); return
        
        try:
            database.adicionar_usuario(user, p1, nivel)
            messagebox.showinfo("Sucesso", f"Usuário '{user}' criado com sucesso.", parent=janela_cad_user)
            janela_cad_user.destroy()
            callback_atualizar()
        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=janela_cad_user)
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao criar usuário: {e}", parent=janela_cad_user)

    ttk.Button(frame, text="Salvar", command=salvar_novo_usuario).grid(row=8, column=0, sticky='e', pady=15)

def abrir_janela_gerenciar_usuarios(janela_principal):
    """Abre a janela de gerenciamento de usuários para o admin."""
    janela_users = tk.Toplevel(janela_principal)
    janela_users.title("Gerenciamento de Usuários")
    janela_users.geometry("600x400")
    janela_users.transient(janela_principal)
    janela_users.grab_set()

    frame = ttk.Frame(janela_users, padding="10")
    frame.pack(expand=True, fill='both')

    tree_frame = ttk.Frame(frame)
    tree_frame.pack(expand=True, fill='both', pady=(0, 10))
    cols = ('ID', 'Nome de Usuário', 'Nível de Acesso')
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings')

    tree.heading('ID', text='ID'); tree.column('ID', width=50, anchor='center')
    tree.heading('Nome de Usuário', text='Nome de Usuário'); tree.column('Nome de Usuário', width=250)
    tree.heading('Nível de Acesso', text='Nível de Acesso'); tree.column('Nível de Acesso', width=150, anchor='center')
    tree.grid(row=0, column=0, sticky='nsew')
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')
    tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)

    def recarregar_lista():
        for i in tree.get_children(): tree.delete(i)
        try:
            for user in database.listar_usuarios():
                tree.insert("", "end", values=(user['id'], user['nome_usuario'], user['nivel_acesso']))
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}", parent=janela_users)

    def excluir_selecionado():
        selected_item = tree.focus()
        if not selected_item: return
        
        user_id = tree.item(selected_item)['values'][0]
        user_nome = tree.item(selected_item)['values'][1]

        if user_id == USUARIO_LOGADO['id']:
            messagebox.showerror("Ação Inválida", "Você não pode excluir o seu próprio usuário.", parent=janela_users)
            return

        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o usuário '{user_nome}'?", parent=janela_users):
            try:
                database.excluir_usuario(user_id)
                recarregar_lista()
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir usuário: {e}", parent=janela_users)

    botoes_frame = ttk.Frame(frame)
    botoes_frame.pack(fill='x', side='bottom')
    ttk.Button(botoes_frame, text="Adicionar Novo", command=lambda: abrir_janela_cadastro_usuario(janela_users, recarregar_lista)).pack(side='left', padx=5)
    ttk.Button(botoes_frame, text="Excluir Selecionado", command=excluir_selecionado).pack(side='left', padx=5)

    recarregar_lista()
    

def abrir_janela_principal():
    """Cria e exibe a janela principal da aplicação após o login."""
    try:
        # Inicializa o banco de dados, criando e/ou atualizando as tabelas necessárias.
        database.inicializar_banco_de_dados()
    except Exception as e:
        # Se a inicialização do DB falhar, é um erro crítico.
        # Mostra uma mensagem de erro clara e encerra o programa.
        root_error = tk.Tk()
        root_error.withdraw()  # Oculta a janela raiz vazia
        messagebox.showerror("Erro Crítico de Inicialização", f"Ocorreu um erro ao preparar o banco de dados:\n\n{e}\n\nO programa será encerrado.")
        return # Impede que o resto do programa execute

    root = tk.Tk()
    root.title("Sistema de Clínica - Início")
    root.geometry("800x500") # Aumentei o tamanho para caber o calendário

    # --- Layout com Frames ---
    top_frame = tk.Frame(root, pady=10)
    top_frame.pack(fill='x', padx=10, anchor='n')
    tk.Label(top_frame, text="Sistema de Acompanhamento Terapêutico", font=("Helvetica", 16, "bold")).pack(side='left', expand=True)
    if USUARIO_LOGADO:
        user_info = f"Usuário: {USUARIO_LOGADO['nome_usuario']} ({USUARIO_LOGADO['nivel_acesso']})"
        tk.Label(top_frame, text=user_info, font=("Helvetica", 9)).pack(side='right')

    main_content_frame = tk.Frame(root)
    main_content_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Frame da Esquerda para os botões
    left_frame = tk.Frame(main_content_frame, width=200)
    left_frame.pack(side='left', fill='y', padx=(0, 10))
    left_frame.pack_propagate(False) # Impede que o frame encolha para o tamanho dos botões

    # Frame da Direita para o calendário
    right_frame = tk.Frame(main_content_frame)
    right_frame.pack(side='right', fill='both', expand=True)

    # --- Botões de Ação (no frame da esquerda) ---
    btn_cadastrar = tk.Button(left_frame, text="Cadastrar Paciente", font=("Helvetica", 11), command=lambda: abrir_janela_cadastro(root))
    btn_cadastrar.pack(pady=5, fill='x')

    # Botões visíveis apenas para o administrador
    if USUARIO_LOGADO and USUARIO_LOGADO['nivel_acesso'] == 'admin':
        btn_medicos = tk.Button(left_frame, text="Gerenciar Médicos", font=("Helvetica", 11), command=lambda: abrir_janela_lista_medicos(root))
        btn_medicos.pack(pady=5, fill='x')
        btn_gerenciar_usuarios = tk.Button(left_frame, text="Gerenciar Usuários", font=("Helvetica", 11), command=lambda: abrir_janela_gerenciar_usuarios(root))
        btn_gerenciar_usuarios.pack(pady=5, fill='x')

    def atualizar_eventos_calendario(calendario):
        """Busca as datas com sessões e as marca no calendário."""
        # Limpa todos os eventos antigos para não duplicar
        calendario.calevent_remove('all')
        
        datas_sessoes = database.listar_datas_sessoes()
        for data_str in datas_sessoes:
            try:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
                # Cria um evento naquela data com uma tag específica
                calendario.calevent_create(data_obj, 'Sessão Agendada', tags='sessao_marcada')
            except (ValueError, TypeError):
                continue # Ignora datas em formato inválido

    # --- Calendário (no frame da direita) ---
    # Configura o estilo da tag que vamos usar para marcar os dias
    

    # --- Calendário (no frame da direita) ---
    hoje = date.today()
    cal = Calendar(right_frame, selectmode='day', year=hoje.year, month=hoje.month, day=hoje.day,
                   locale='pt_BR', # Tenta usar o idioma Português (requer que o locale esteja instalado no sistema)
                   date_pattern='dd/mm/y')
    cal.pack(fill="both", expand=True)
    # Configura a cor da nossa tag de evento
    cal.tag_config('sessao_marcada', background='lightblue', foreground='black')

    # Botão de Listar Pacientes (precisa do callback do calendário)
    btn_listar = tk.Button(left_frame, text="Listar Pacientes", font=("Helvetica", 11), command=lambda: abrir_janela_lista(root, lambda: atualizar_eventos_calendario(cal)))
    btn_listar.pack(pady=5, fill='x')

    # Carrega os eventos no calendário pela primeira vez
    atualizar_eventos_calendario(cal)

    root.mainloop()

def abrir_janela_login():
    """Abre a janela de login inicial do sistema."""
    login_window = tk.Tk()
    login_window.title("Login - Sistema de Clínica")
    login_window.geometry("350x180")
    login_window.resizable(False, False)

    # Centraliza a janela na tela
    window_width, window_height = 350, 180
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    login_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    frame = ttk.Frame(login_window, padding="20")
    frame.pack(expand=True, fill='both')

    ttk.Label(frame, text="Nome de Usuário:").pack(anchor='w')
    entry_user = ttk.Entry(frame, width=30)
    entry_user.pack(fill='x', pady=(0, 10))
    entry_user.focus_set()

    ttk.Label(frame, text="Senha:").pack(anchor='w')
    entry_pass = ttk.Entry(frame, width=30, show="*")
    entry_pass.pack(fill='x', pady=(0, 15))

    def tentar_login():
        usuario = entry_user.get().strip()
        senha = entry_pass.get().strip()
        if not usuario or not senha:
            messagebox.showerror("Erro", "Usuário e senha são obrigatórios.", parent=login_window)
            return

        usuario_valido = database.verificar_usuario(usuario, senha)
        if usuario_valido:
            global USUARIO_LOGADO
            USUARIO_LOGADO = usuario_valido
            login_window.destroy()
            abrir_janela_principal()
        else:
            messagebox.showerror("Falha no Login", "Nome de usuário ou senha incorretos.", parent=login_window)

    entry_pass.bind("<Return>", lambda event: tentar_login())
    ttk.Button(frame, text="Login", command=tentar_login).pack(fill='x')
    login_window.mainloop()

def main():
    """Função principal que inicializa o DB e chama a tela de login."""
    try:
        database.inicializar_banco_de_dados()
    except Exception as e:
        root_error = tk.Tk(); root_error.withdraw()
        messagebox.showerror("Erro Crítico", f"Erro ao inicializar o banco de dados:\n\n{e}")
        return
    abrir_janela_login()

if __name__ == "__main__":
    main()