# -*- coding: utf-8 -*-
import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import sys
import os

# Carregar a chave secreta
with open("secret.key", "rb") as key_file:
    secret_key = key_file.read()

# Inicializar o objeto de criptografia com a chave
cipher = Fernet(secret_key)

# Descriptografar o conteúdo do arquivo .env.enc
with open(".env.enc", "rb") as enc_file:
    decrypted = cipher.decrypt(enc_file.read())

# Converter o conteúdo descriptografado em variáveis
env_vars = dict(line.split('=') for line in decrypted.decode().splitlines())

# Configurações do Banco de Dados
DB_CONFIG = {
    "host": env_vars.get("DB_HOST"),
    "database": env_vars.get("DB_NAME"),
    "user": env_vars.get("DB_USER"),
    "password": env_vars.get("DB_PASSWORD"),
}

# Função para conectar ao banco de dados
def connect_to_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        messagebox.showerror("Erro", f"Erro na conexão com o banco de dados: {e}")
        return None

# Função para carregar dados na tabela
def load_data(tree, search_term=None):
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()

        # Filtrar ou carregar todos os registros
        if search_term:
            cursor.execute("""SELECT * FROM computadores WHERE 
                LOWER(filial) LIKE LOWER(%s) OR LOWER(setor) LIKE LOWER(%s) OR LOWER(usuario) LIKE LOWER(%s)
                OR LOWER(tipo_pc) LIKE LOWER(%s) OR LOWER(processador) LIKE LOWER(%s) 
                OR LOWER(modelo) LIKE LOWER(%s) OR LOWER(disco_armazenamento) LIKE LOWER(%s)
                OR LOWER(tipo_disco) LIKE LOWER(%s) OR LOWER(memoria_ram) LIKE LOWER(%s)
                OR LOWER(tipo_memoria) LIKE LOWER(%s) OR LOWER(observacoes) LIKE LOWER(%s);""",
                tuple([f"%{search_term}%"] * 11))
        else:
            cursor.execute("SELECT * FROM computadores;")

        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)
        cursor.close()
    except Exception as e:
        print("Erro ao carregar dados:", e)
        messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
    finally:
        conn.close()
# Função para validar os campos
def validate_fields(fields):
    for field, var in fields.items():
        if not var.get():
            messagebox.showwarning("Aviso", f"O campo '{field}' está vazio!")
            return False
    return True

# Função para adicionar registro
def add_record(tree):
    def save_record():
        if not validate_fields(vars_dict):
            return

        conn = connect_to_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()

            # Log dos valores enviados
            print("Valores enviados para o banco:")
            for key, value in vars_dict.items():
                print(f"{key}: {value.get()}")

            # Executar o comando SQL
            cursor.execute("""
                INSERT INTO computadores (filial, setor, usuario, tipo_pc, processador, modelo, 
                                         disco_armazenamento, tipo_disco, memoria_ram, tipo_memoria, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                vars_dict["filial"].get(), vars_dict["setor"].get(), vars_dict["usuario"].get(),
                vars_dict["tipo_pc"].get(), vars_dict["processador"].get(), vars_dict["modelo"].get(),
                vars_dict["disco_armazenamento"].get(), vars_dict["tipo_disco"].get(),
                vars_dict["memoria_ram"].get(), vars_dict["tipo_memoria"].get(),
                vars_dict["observacoes"].get()
            ))

            conn.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Registro adicionado com sucesso!")
            add_window.destroy()
            load_data(tree)
        except Exception as e:
            print("Erro ao adicionar registro:", e)
            messagebox.showerror("Erro", f"Erro ao adicionar registro: {e}")
        finally:
            conn.close()

    # Janela para adicionar registro
    add_window = tk.Toplevel(root)
    add_window.title("Adicionar Registro")
    add_window.geometry("500x600")
    add_window.configure(bg="#030028")

    # Lista de campos
    fields = [
        ("Filial", ["FOR", "SLZ", "SOB", "THE", "IMP", "JUA"], ""),
        ("Setor", None, ""),
        ("Usuario", None, ""),  # Removido acento
        ("Tipo PC", ["Desktop", "Notebook", "Servidor"], ""),
        ("Processador", None, ""),
        ("Modelo", None, ""),
        ("Disco Armazenamento", None, ""),
        ("Tipo Disco", ["HDD", "SSD", "HD + SSD"], ""),
        ("Memoria RAM", None, ""),  # Removido acento
        ("Tipo Memoria", ["DDR3", "DDR4", "DDR5"], ""),  # Removido acento
        ("Observacoes", None, "")  # Removido acento
    ]

    # Dicionário de variáveis
    vars_dict = {}
    for idx, (label, options, default) in enumerate(fields):
        tk.Label(add_window, text=label, bg="#030028", fg="white", font=("Arial", 12)).grid(row=idx, column=0, padx=10, pady=5, sticky="e")
        var = tk.StringVar(value=default)
        vars_dict[label.lower().replace(" ", "_")] = var

        if options:
            ttk.Combobox(add_window, textvariable=var, values=options, state="readonly", width=30).grid(row=idx, column=1, padx=10, pady=5)
        else:
            tk.Entry(add_window, textvariable=var, width=30).grid(row=idx, column=1, padx=10, pady=5)

    tk.Button(add_window, text="Salvar", command=save_record, bg="#0066CC", fg="white").grid(row=len(fields), column=0, columnspan=2, pady=10)

# Função para carregar dados
def load_data(tree, search_term=None):
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()

        # Filtrar ou carregar todos os registros
        if search_term:
            cursor.execute("""SELECT * FROM computadores WHERE 
                LOWER(filial) LIKE LOWER(%s) OR LOWER(setor) LIKE LOWER(%s) OR LOWER(usuario) LIKE LOWER(%s)
                OR LOWER(tipo_pc) LIKE LOWER(%s) OR LOWER(processador) LIKE LOWER(%s) 
                OR LOWER(modelo) LIKE LOWER(%s) OR LOWER(disco_armazenamento) LIKE LOWER(%s)
                OR LOWER(tipo_disco) LIKE LOWER(%s) OR LOWER(memoria_ram) LIKE LOWER(%s)
                OR LOWER(tipo_memoria) LIKE LOWER(%s) OR LOWER(observacoes) LIKE LOWER(%s);""",
                tuple([f"%{search_term}%"] * 11))
        else:
            cursor.execute("SELECT * FROM computadores;")

        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)
        cursor.close()
    except Exception as e:
        print("Erro ao carregar dados:", e)
        messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
    finally:
        conn.close()

# Função para editar registro
def edit_record(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Aviso", "Nenhum registro selecionado para edição!")
        return

    item = tree.item(selected_item)
    record = item['values']

    def save_edit():
        conn = connect_to_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE computadores
                SET filial = %s, setor = %s, usuario = %s, tipo_pc = %s, processador = %s, modelo = %s,
                    disco_armazenamento = %s, tipo_disco = %s, memoria_ram = %s, tipo_memoria = %s, observacoes = %s
                WHERE id = %s;
            """, (
                vars_dict["filial"].get(), vars_dict["setor"].get(), vars_dict["usuario"].get(),
                vars_dict["tipo_pc"].get(), vars_dict["processador"].get(), vars_dict["modelo"].get(),
                vars_dict["disco_armazenamento"].get(), vars_dict["tipo_disco"].get(),
                vars_dict["memoria_ram"].get(), vars_dict["tipo_memoria"].get(),
                vars_dict["observacoes"].get(), record[0]
            ))

            conn.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Registro editado com sucesso!")
            edit_window.destroy()
            load_data(tree)
        except Exception as e:
            print("Erro ao editar registro:", e)
            messagebox.showerror("Erro", f"Erro ao editar registro: {e}")
        finally:
            conn.close()

    # Janela para editar registro
    edit_window = tk.Toplevel(root)
    edit_window.title("Editar Registro")
    edit_window.geometry("500x600")
    edit_window.configure(bg="#030028")

    fields = [
        ("Filial", ["FOR", "SLZ", "SOB", "THE", "IMP", "JUA"], record[1]),
        ("Setor", None, record[2]),
        ("Usuario", None, record[3]),
        ("Tipo PC", ["Desktop", "Notebook", "Servidor"], record[4]),
        ("Processador", None, record[5]),
        ("Modelo", None, record[6]),
        ("Disco Armazenamento", None, record[7]),
        ("Tipo Disco", ["HDD", "SSD", "HD + SSD"], record[8]),
        ("Memoria RAM", None, record[9]),
        ("Tipo Memoria", ["DDR3", "DDR4", "DDR5"], record[10]),
        ("Observacoes", None, record[11])
    ]

    vars_dict = {}
    for idx, (label, options, default) in enumerate(fields):
        tk.Label(edit_window, text=label, bg="#030028", fg="white", font=("Arial", 12)).grid(row=idx, column=0, padx=10, pady=5, sticky="e")
        var = tk.StringVar(value=default)
        vars_dict[label.lower().replace(" ", "_")] = var

        if options:
            ttk.Combobox(edit_window, textvariable=var, values=options, state="readonly", width=30).grid(row=idx, column=1, padx=10, pady=5)
        else:
            tk.Entry(edit_window, textvariable=var, width=30).grid(row=idx, column=1, padx=10, pady=5)

    tk.Button(edit_window, text="Salvar", command=save_edit, bg="#0066CC", fg="white").grid(row=len(fields), column=0, columnspan=2, pady=10)


# Função para excluir registro
def delete_record(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Aviso", "Nenhum registro selecionado para exclusão!")
        return

    item = tree.item(selected_item)
    record_id = item['values'][0]

    if messagebox.askyesno("Confirmação", "Tem certeza de que deseja excluir este registro?"):
        conn = connect_to_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM computadores WHERE id = %s;", (record_id,))
            conn.commit()
            cursor.close()
            messagebox.showinfo("Sucesso", "Registro excluído com sucesso!")
            load_data(tree)
        except Exception as e:
            print("Erro ao excluir registro:", e)
            messagebox.showerror("Erro", f"Erro ao excluir registro: {e}")
        finally:
            conn.close()

# Interface principal
root = tk.Tk()
root.title("Gerenciamento de Computadores")
root.geometry("1200x700")
root.configure(bg="#030028")


# Logo
logo_frame = tk.Frame(root, bg="#030028")
logo_frame.pack(fill="x", pady=10)
try:
    image_path = "./img/01.jpg"  # Atualize o caminho se necessário
    logo_img = Image.open(image_path).resize((150, 100))
    logo_photo = ImageTk.PhotoImage(logo_img)
    tk.Label(logo_frame, image=logo_photo, bg="#030028").pack()
except Exception as e:
    messagebox.showwarning("Aviso", "Imagem não encontrada.")

# Campo de pesquisa
search_var = tk.StringVar()
tk.Entry(root, textvariable=search_var, width=70).pack(pady=10)
tk.Button(root, text="Pesquisar", command=lambda: load_data(tree, search_var.get()), bg="#0066CC", fg="white").pack(pady=10)

# Tabela
columns = ["ID", "Filial", "Setor", "Usuario", "Tipo PC", "Processador", "Modelo", 
           "Disco Armazenamento", "Tipo Disco", "Memoria RAM", "Tipo Memoria", "Observacoes"]
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100 if col == "ID" else 150)
tree.pack(pady=20, fill="both", expand=True)

# Botões
btn_frame = tk.Frame(root, bg="#030028")
btn_frame.pack(pady=10, fill="x")

tk.Button(btn_frame, text="Adicionar", command=lambda: add_record(tree), bg="#0066CC", fg="white").pack(side="left", padx=10)
tk.Button(btn_frame, text="Editar", command=lambda: edit_record(tree), bg="#0066CC", fg="white").pack(side="left", padx=10)
tk.Button(btn_frame, text="Excluir", command=lambda: delete_record(tree), bg="#FF0000", fg="white").pack(side="left", padx=10)

# Carregar dados
load_data(tree)
root.mainloop()