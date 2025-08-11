import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
import database  # Importa nosso módulo de banco de dados

def salvar_paciente(janela_cadastro, entry_nome, entry_data, entry_resp):
    """Coleta os dados dos campos de entrada e salva no banco de dados."""
    nome = entry_nome.get()
    data_nasc = entry_data.get()
    responsavel = entry_resp.get()

    if not nome or not data_nasc or not responsavel:
        messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios!", parent=janela_cadastro)
        return

    try:
        database.adicionar_paciente(nome, data_nasc, responsavel)
        messagebox.showinfo("Sucesso", f"Paciente {nome} cadastrado com sucesso!", parent=janela_cadastro)
        janela_cadastro.destroy()
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar: {e}", parent=janela_cadastro)

def salvar_alteracoes_paciente(janela_edicao, entry_nome, entry_data, entry_resp, paciente_id):
    """Salva as alterações de um paciente existente."""
    nome = entry_nome.get()
    data_nasc = entry_data.get()
    responsavel = entry_resp.get()

    if not nome or not data_nasc or not responsavel:
        messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios!", parent=janela_edicao)
        return

    try:
        database.atualizar_paciente(paciente_id, nome, data_nasc, responsavel)
        messagebox.showinfo("Sucesso", "Dados do paciente atualizados com sucesso!", parent=janela_edicao)
        janela_edicao.destroy()
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao atualizar: {e}", parent=janela_edicao)

def salvar_nova_sessao(janela_form, paciente_id, widgets):
    """Salva uma nova sessão no banco de dados."""
    try:
        data_sessao = widgets['data'].get()
        resumo = widgets['resumo'].get("1.0", "end-1c")
        foco = widgets['foco'].get("1.0", "end-1c")
        evolucao = widgets['evolucao'].get()
        seg = widgets['seg'].get()
        ter = widgets['ter'].get()
        qua = widgets['qua'].get()
        qui = widgets['qui'].get()
        sex = widgets['sex'].get()

        if not data_sessao:
            messagebox.showerror("Erro de Validação", "O campo 'Data da Sessão' é obrigatório.", parent=janela_form)
            return

        database.adicionar_sessao(paciente_id, data_sessao, resumo, foco, evolucao, seg, ter, qua, qui, sex)
        messagebox.showinfo("Sucesso", "Nova sessão registrada com sucesso!", parent=janela_form)
        janela_form.destroy()
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar a sessão: {e}", parent=janela_form)

def salvar_alteracoes_sessao(janela_form, sessao_id, widgets):
    """Salva as alterações de uma sessão existente."""
    data_sessao = widgets['data'].get()
    resumo = widgets['resumo'].get("1.0", "end-1c")
    foco = widgets['foco'].get("1.0", "end-1c")
    evolucao = widgets['evolucao'].get()
    seg = widgets['seg'].get()
    ter = widgets['ter'].get()
    qua = widgets['qua'].get()
    qui = widgets['qui'].get()
    sex = widgets['sex'].get()

    if not data_sessao:
        messagebox.showerror("Erro de Validação", "O campo 'Data da Sessão' é obrigatório.", parent=janela_form)
        return
    try:
        database.atualizar_sessao(sessao_id, data_sessao, resumo, foco, evolucao, seg, ter, qua, qui, sex)
        messagebox.showinfo("Sucesso", "Sessão atualizada com sucesso!", parent=janela_form)
        janela_form.destroy()
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar a sessão: {e}", parent=janela_form)


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

    tk.Label(frame, text="Data de Nascimento:").grid(row=1, column=0, sticky="w", pady=5)
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
    entry_nome.insert(0, paciente_data[1])  # nome_completo

    tk.Label(frame, text="Data de Nascimento:").grid(row=1, column=0, sticky="w", pady=5)
    entry_data = tk.Entry(frame, width=40)
    entry_data.grid(row=1, column=1, pady=5)
    entry_data.insert(0, paciente_data[2])  # data_nascimento

    tk.Label(frame, text="Nome do Responsável:").grid(row=2, column=0, sticky="w", pady=5)
    entry_resp = tk.Entry(frame, width=40)
    entry_resp.grid(row=2, column=1, pady=5)
    entry_resp.insert(0, paciente_data[3])  # nome_responsavel

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

    # Aba 1: Resumo e Foco
    aba1 = ttk.Frame(notebook, padding=10)
    notebook.add(aba1, text=' Resumo e Foco ')

    # Aba 2: Plano Semanal e Evolução
    aba2 = ttk.Frame(notebook, padding=10)
    notebook.add(aba2, text=' Plano Semanal e Evolução ')

    # --- Widgets da Aba 1 ---
    ttk.Label(aba1, text="Resumo da Sessão:").pack(anchor='w')
    text_resumo = tk.Text(aba1, width=50, height=10, wrap='word')
    text_resumo.pack(expand=True, fill='both', pady=(0, 10))

    ttk.Label(aba1, text="Foco para Próxima Sessão:").pack(anchor='w')
    text_foco = tk.Text(aba1, width=50, height=6, wrap='word')
    text_foco.pack(expand=True, fill='both')

    # --- Widgets da Aba 2 ---
    frame_evolucao = ttk.Frame(aba2)
    frame_evolucao.pack(fill='x', pady=(0, 15))
    ttk.Label(frame_evolucao, text="Nível de Evolução:").pack(side='left')
    combo_evolucao = ttk.Combobox(frame_evolucao, values=["Iniciante", "Intermediário", "Avançado", "Manutenção"])
    combo_evolucao.pack(side='left', padx=5)

    frame_plano = ttk.LabelFrame(aba2, text="Plano de Terapias Semanais", padding=10)
    frame_plano.pack(fill='both', expand=True)

    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]
    entradas_dias = {}
    for i, dia in enumerate(dias):
        ttk.Label(frame_plano, text=f"{dia}:").grid(row=i, column=0, sticky='w', pady=2)
        entry = ttk.Entry(frame_plano, width=40)
        entry.grid(row=i, column=1, sticky='ew', padx=5)
        entradas_dias[dia[:3].lower()] = entry
    frame_plano.columnconfigure(1, weight=1)

    return {
        "resumo": text_resumo, "foco": text_foco, "evolucao": combo_evolucao,
        "seg": entradas_dias['seg'], "ter": entradas_dias['ter'], "qua": entradas_dias['qua'],
        "qui": entradas_dias['qui'], "sex": entradas_dias['sex']
    }

def abrir_janela_detalhes_sessao(janela_pai, sessao_id):
    """Abre uma janela para exibir os detalhes completos de uma sessão."""
    sessao_data = database.buscar_sessao_por_id(sessao_id)
    if not sessao_data:
        messagebox.showerror("Erro", "Sessão não encontrada.", parent=janela_pai)
        return
    
    janela_detalhes = tk.Toplevel(janela_pai)
    janela_detalhes.title(f"Detalhes da Sessão - {sessao_data[0]}")
    janela_detalhes.geometry("600x500")
    janela_detalhes.resizable(False, False)
    janela_detalhes.transient(janela_pai)
    janela_detalhes.grab_set()

    frame = ttk.Frame(janela_detalhes, padding="15")
    frame.pack(expand=True, fill='both')
    
    widgets = criar_abas_sessao(frame)
    
    # Preenche os dados e desabilita a edição
    widgets['resumo'].insert('1.0', sessao_data[1] or "")
    widgets['foco'].insert('1.0', sessao_data[2] or "")
    widgets['evolucao'].set(sessao_data[3] or "")
    widgets['seg'].insert(0, sessao_data[4] or "")
    widgets['ter'].insert(0, sessao_data[5] or "")
    widgets['qua'].insert(0, sessao_data[6] or "")
    widgets['qui'].insert(0, sessao_data[7] or "")
    widgets['sex'].insert(0, sessao_data[8] or "")

    for w in widgets.values():
        if isinstance(w, (tk.Text, ttk.Entry, ttk.Combobox)):
            w.config(state='disabled')

    ttk.Button(frame, text="Fechar", command=janela_detalhes.destroy).pack(side='bottom', pady=(10, 0))

def abrir_janela_sessoes(janela_pai, paciente_id, paciente_nome):
    """Abre uma janela para listar e gerenciar as sessões de um paciente."""
    janela_sessoes = tk.Toplevel(janela_pai)
    janela_sessoes.title(f"Sessões de {paciente_nome}")
    janela_sessoes.geometry("800x500")
    janela_sessoes.transient(janela_pai)
    janela_sessoes.grab_set()

    frame = ttk.Frame(janela_sessoes, padding="10")
    frame.pack(expand=True, fill='both')

    # Tabela de Sessões
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(expand=True, fill='both')
    cols = ('ID', 'Data da Sessão', 'Nível de Evolução', 'Resumo')
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings')

    tree.heading('ID', text='ID')
    tree.column('ID', width=50, anchor='center')
    tree.heading('Data da Sessão', text='Data da Sessão')
    tree.column('Data da Sessão', width=150, anchor='center')
    tree.heading('Nível de Evolução', text='Nível de Evolução')
    tree.column('Nível de Evolução', width=150, anchor='center')
    tree.heading('Resumo', text='Resumo da Sessão')
    tree.column('Resumo', width=450)

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
                # sessao = (id, data, evolucao, resumo)
                # Limita o resumo para exibição na tabela e remove quebras de linha
                resumo_original = sessao[3] if sessao[3] else ""
                resumo_curto = (resumo_original[:75] + '...') if len(resumo_original) > 75 else resumo_original
                tree.insert("", "end", values=(sessao[0], sessao[1], sessao[2], resumo_curto.replace('\n', ' ')))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar sessões: {e}", parent=janela_sessoes)

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
        command=lambda: abrir_janela_nova_sessao(janela_sessoes, paciente_id, recarregar_sessoes)
    )
    btn_adicionar.pack(side='left', padx=5)
    
    def editar_sessao_selecionada():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma sessão para editar.", parent=janela_sessoes)
            return
        sessao_id = tree.item(selected_item)['values'][0]
        abrir_janela_edicao_sessao(janela_sessoes, sessao_id, recarregar_sessoes)

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
                recarregar_sessoes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir sessão: {e}", parent=janela_sessoes)

    ttk.Button(botoes_frame, text="Editar Sessão", command=editar_sessao_selecionada).pack(side='left', padx=5)
    ttk.Button(botoes_frame, text="Excluir Sessão", command=excluir_sessao_selecionada).pack(side='left', padx=5)

    # Carrega os dados iniciais
    recarregar_sessoes()

def abrir_janela_nova_sessao(janela_pai, paciente_id, callback_atualizar, sessao_id=None):
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
    ttk.Label(frame_data, text="Data da Sessão:").pack(side='left')
    entry_data = ttk.Entry(frame_data, width=20)
    entry_data.pack(side='left', padx=5)
    
    widgets = criar_abas_sessao(frame)
    widgets['data'] = entry_data # Adiciona a entrada de data ao dicionário

    if sessao_id: # Modo de edição
        sessao_data = database.buscar_sessao_por_id(sessao_id)
        entry_data.insert(0, sessao_data[0])
        widgets['resumo'].insert('1.0', sessao_data[1] or "")
        widgets['foco'].insert('1.0', sessao_data[2] or "")
        widgets['evolucao'].set(sessao_data[3] or "")
        widgets['seg'].insert(0, sessao_data[4] or "")
        widgets['ter'].insert(0, sessao_data[5] or "")
        widgets['qua'].insert(0, sessao_data[6] or "")
        widgets['qui'].insert(0, sessao_data[7] or "")
        widgets['sex'].insert(0, sessao_data[8] or "")
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
    abrir_janela_nova_sessao(janela_pai, paciente_id=None, callback_atualizar=callback_atualizar, sessao_id=sessao_id)

def abrir_janela_lista(janela_principal):
    """Abre uma janela para listar todos os pacientes."""
    janela_lista = tk.Toplevel(janela_principal)
    janela_lista.title("Lista de Pacientes Cadastrados")
    janela_lista.geometry("800x450")
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
    cols = ('ID', 'Nome Completo', 'Data de Nascimento', 'Responsável') # Colunas visíveis
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)

    # Configura os cabeçalhos e larguras das colunas
    tree.heading('ID', text='ID')
    tree.column('ID', width=50, anchor='center')
    tree.heading('Nome Completo', text='Nome Completo')
    tree.column('Nome Completo', width=300)
    tree.heading('Data de Nascimento', text='Data de Nascimento')
    tree.column('Data de Nascimento', width=150, anchor='center')
    tree.heading('Responsável', text='Responsável')
    tree.column('Responsável', width=250)

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
                tree.insert("", "end", values=paciente)
        except Exception as e:
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
        abrir_janela_sessoes(janela_lista, paciente_id, paciente_nome)

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
            except Exception as e:
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
    ttk.Button(botoes_frame, text="Ver Sessões", command=ver_sessoes_selecionado).pack(side='right', padx=5)

    # Carrega os dados iniciais na tabela
    recarregar_lista()


def main():
    """Função principal que cria a interface e inicia o loop do aplicativo."""
    database.criar_tabela_pacientes()
    database.criar_tabela_sessoes()

    root = tk.Tk()
    root.title("Sistema de Clínica - Início")
    root.geometry("500x300")

    tk.Label(root, text="Sistema de Acompanhamento Terapêutico", font=("Helvetica", 16, "bold")).pack(pady=30)

    btn_cadastrar = tk.Button(root, text="Cadastrar Novo Paciente", font=("Helvetica", 12), width=30, height=2, command=lambda: abrir_janela_cadastro(root))
    btn_cadastrar.pack(pady=10)

    btn_listar = tk.Button(root, text="Listar Pacientes", font=("Helvetica", 12), width=30, height=2, command=lambda: abrir_janela_lista(root))
    btn_listar.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
