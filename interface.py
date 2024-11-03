# interface.py
import tkinter as tk
from tkinter import messagebox
import threading
import time
import mu_automation  # Importa o arquivo mu_automation com as funções de automação

# Variável global para controlar a execução da automação
automation_running = False

# Função para iniciar a automação
def start_automation():
    global automation_running
    if not automation_running:
        automation_running = True
        countdown_label.config(text="Iniciando...")
        # Inicia a automação em uma nova thread
        automation_thread = threading.Thread(target=automation_interface_loop)
        automation_thread.daemon = True  # Permite que o programa feche mesmo com a thread ativa
        automation_thread.start()
    else:
        messagebox.showinfo("Automação", "A automação já está em execução.")

# Função para parar a automação
def stop_automation():
    global automation_running
    automation_running = False
    countdown_label.config(text="Automação pausada.")

# Função para contagem regressiva com atualização no label
def countdown(seconds):
    while seconds > 0 and automation_running:
        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02}:{secs:02}"
        countdown_label.config(text=f"Iniciando nova execução em: {timer}")
        time.sleep(1)
        seconds -= 1
    if automation_running:
        countdown_label.config(text="Executando comandos...")

# Função de automação da interface
def automation_interface_loop():
    while automation_running:
        # Executa uma contagem regressiva de 10 segundos antes de cada execução
        countdown(10)  # Altere o valor para o tempo desejado entre execuções
        
        # Foca a janela do jogo e executa os comandos
        focus_attempts = 0
        while focus_attempts < 10 and automation_running:
            if mu_automation.focus_game_window():  # Tenta focar a janela
                print("Janela focada com sucesso, iniciando automação...")
                mu_automation.execute_commands()  # Executa os comandos
                break
            else:
                print(f"Tentativa {focus_attempts + 1} de 10 para focar a janela...")
                focus_attempts += 1
                time.sleep(1)  # Aguardar 1 segundo entre as tentativas

        if focus_attempts == 10:
            print("Falha ao focar a janela após 10 tentativas. Verifique se o jogo está aberto.")
            countdown_label.config(text="Falha ao focar a janela.")

        # Contagem regressiva de 30 segundos antes da próxima execução
        countdown(30)  # Altere o valor aqui para definir o intervalo desejado entre execuções

# Configuração da interface Tkinter
root = tk.Tk()
root.title("Controle de Automação")
root.geometry("300x200")

# Botão para iniciar a automação
start_button = tk.Button(root, text="Iniciar Automação", command=start_automation, bg="green", fg="white")
start_button.pack(pady=10)

# Botão para parar a automação
stop_button = tk.Button(root, text="Parar Automação", command=stop_automation, bg="red", fg="white")
stop_button.pack(pady=10)

# Label para exibir a contagem regressiva
countdown_label = tk.Label(root, text="Automação pausada.", font=("Helvetica", 12))
countdown_label.pack(pady=20)

# Iniciar o loop da interface
root.mainloop()
