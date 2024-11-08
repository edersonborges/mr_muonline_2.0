import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import os
import pyautogui  # Certifique-se de que está instalado e funcionando

# Atualize os imports para o novo caminho
import automation.mu_automation as mu_automation
import config.config_manager as config_manager
import automation.image_processing as image_processing
from utils.timer import countdown  # Se você criar countdown como função em timer.py


# Variáveis globais para configuração
LEVEL_AREA_OFFSET_LEFT = 550
LEVEL_AREA_OFFSET_TOP = 90
LEVEL_AREA_WIDTH = 150
LEVEL_AREA_HEIGHT = 30

NICK_AREA_OFFSET_LEFT = 600
NICK_AREA_OFFSET_TOP = 35
NICK_AREA_WIDTH = 150
NICK_AREA_HEIGHT = 23

# Variável global de estado
automation_running = False

class MuAutomation:
    def __init__(self):
        self.automation_count = 0
        self.last_level_checked = None
        self.last_nick_checked = None
        self.screenshot_folder = ""
        self.required_level = 0
        self.window_name = ""
        self.check_interval = 0
        self.required_nick = ""

    def start_automation(self):
        """Inicia o processo de automação."""
        global automation_running
        if not automation_running:
            # Coleta valores da interface
            self.screenshot_folder = folder_entry.get()
            self.required_level = int(level_entry.get())
            self.window_name = window_name_entry.get()
            self.check_interval = int(interval_entry.get())
            self.required_nick = nick_entry.get()

            if not os.path.isdir(self.screenshot_folder):
                messagebox.showerror("Erro", "Pasta de screenshots inválida.")
                return

            # Salva configurações iniciais e inicia thread de automação
            config_manager.save_config(
                self.screenshot_folder, self.required_level, self.window_name,
                self.check_interval, self.automation_count, self.required_nick
            )
            automation_running = True
            threading.Thread(target=self.automation_loop).start()
        else:
            messagebox.showinfo("Automação", "A automação já está em execução.")

    def automation_loop(self):
        """Loop principal da automação."""
        global automation_running
        while automation_running:
            if not mu_automation.focus_game_window(self.window_name):
                print("Falha ao focar na janela do jogo. Tentando novamente em 5 segundos.")
                time.sleep(5)
                continue  # Tenta novamente se o foco falhar

            level_image = image_processing.capture_area(
                self.window_name, LEVEL_AREA_OFFSET_LEFT, LEVEL_AREA_OFFSET_TOP, LEVEL_AREA_WIDTH, LEVEL_AREA_HEIGHT
            )
            nick_image = image_processing.capture_area(
                self.window_name, NICK_AREA_OFFSET_LEFT, NICK_AREA_OFFSET_TOP, NICK_AREA_WIDTH, NICK_AREA_HEIGHT
            )

            level_text = image_processing.get_text_from_image(level_image)
            nick_text = image_processing.get_text_from_image(nick_image)

            # Extrair apenas o número do nível detectado
            try:
                level_number = int(''.join(filter(str.isdigit, level_text)))
                self.last_level_checked = level_number  # Apenas o número do nível
            except ValueError:
                self.last_level_checked = "Não detectado"

            # Atualizar o valor de `last_nick_checked` com o texto completo do nick
            self.last_nick_checked = nick_text

            # Exibe as informações na interface
            update_count_label()
            
            if isinstance(self.last_level_checked, int) and self.last_level_checked >= self.required_level and self.required_nick in nick_text:
                print("Condições atendidas. Iniciando automação...")
                mu_automation.execute_commands(self.window_name)
                self.automation_count += 1
                config_manager.save_config(
                    self.screenshot_folder, 
                    self.required_level, 
                    self.window_name, 
                    self.check_interval, 
                    self.automation_count, 
                    self.required_nick
                )
                update_count_label()
            else:
                print("Condições não atendidas.")
                countdown(countdown_label, self.check_interval)


    def stop_automation(self):
        """Para o processo de automação."""
        global automation_running
        automation_running = False
        print("Automação pausada.")
        update_ui_state(True)

def update_ui_state(enabled=True):
    """Atualiza o estado dos campos de entrada."""
    state = 'normal' if enabled else 'disabled'
    bg_color = 'white' if enabled else 'light gray'
    for widget in [folder_entry, level_entry, window_name_entry, interval_entry, nick_entry]:
        widget.config(state=state, bg=bg_color)

def update_count_label():
    """Atualiza o rótulo do contador de MR e exibe o último Level e Nick verificado."""
    count_label.config(
        text=f"MR Quantidade: {automation.automation_count} | Último Level: {automation.last_level_checked} | Último Nick: {automation.last_nick_checked}"
    )


def countdown(label, seconds):
    """Exibe o countdown de verificação."""
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        label.config(text=f"Próxima verificação em: {mins:02}:{secs:02}")
        time.sleep(1)
    label.config(text="Verificando...")

# Configurações de interface
root = tk.Tk()
root.title("Controle de Automação")
root.geometry("500x600")

automation = MuAutomation()

# Componentes de interface
folder_label = tk.Label(root, text="Pasta de Screenshots:")
folder_entry = tk.Entry(root, width=50)
folder_button = tk.Button(root, text="Selecionar Pasta", command=lambda: folder_entry.insert(0, filedialog.askdirectory()))
level_label = tk.Label(root, text="Level Necessário:")
level_entry = tk.Entry(root, width=5)
window_name_label = tk.Label(root, text="Nome da Janela do Jogo:")
window_name_entry = tk.Entry(root, width=20)
interval_label = tk.Label(root, text="Intervalo de Verificação (segundos):")
interval_entry = tk.Entry(root, width=5)
nick_label = tk.Label(root, text="Nick MR:")
nick_entry = tk.Entry(root, width=20)

# Carregar configurações salvas
folder, level, window, interval, nick, automation_count = config_manager.load_config()
folder_entry.insert(0, folder)
level_entry.insert(0, level)
window_name_entry.insert(0, window)
interval_entry.insert(0, interval)
nick_entry.insert(0, nick)

# Rótulos de contador e aviso
count_label = tk.Label(root, text="MR Quantidade: 0 | Último Level: | Último Nick:", font=("Helvetica", 12))
countdown_label = tk.Label(root, text="Próxima verificação em:")
footer_label = tk.Label(root, text="Desenvolvido por Ed", font=("Helvetica", 8))
footer_label.place(relx=1.0, rely=1.0, anchor="se")
warning_label = tk.Label(root, text="AVISO: O inventário do personagem é limpo a cada MR.", font=("Helvetica", 8), fg="red")

# Botões de controle
start_button = tk.Button(root, text="Iniciar Automação", command=automation.start_automation, bg="green", fg="white", width=20)
stop_button = tk.Button(root, text="Parar Automação", command=automation.stop_automation, bg="red", fg="white", width=20)

# Disposição na interface
for widget in [
    folder_label, folder_entry, folder_button,
    level_label, level_entry, window_name_label, window_name_entry,
    interval_label, interval_entry, nick_label, nick_entry,
    count_label, countdown_label, start_button, stop_button,
    warning_label
]:
    widget.pack(pady=5)

root.mainloop()
