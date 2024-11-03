import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import os
import cv2
import pytesseract
import numpy as np
import pyautogui
import mu_automation  # Importa funções de automação, incluindo focus_game_window
import win32gui
import win32api
import win32con
import mss

# Configura o caminho do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Variáveis globais
automation_running = False
automation_count = 0  # Contador de quantas vezes o Master Reset foi disparado
last_level_checked = None  # Armazena o último nível verificado
last_nick_checked = None  # Armazena o último nick verificado

# Configurações de áreas para Level e Nick
LEVEL_AREA_OFFSET_LEFT = 550
LEVEL_AREA_OFFSET_TOP = 90
LEVEL_AREA_WIDTH = 150
LEVEL_AREA_HEIGHT = 30

NICK_AREA_OFFSET_LEFT = 600
NICK_AREA_OFFSET_TOP = 35
NICK_AREA_WIDTH = 150
NICK_AREA_HEIGHT = 23

# Caminho do arquivo de configuração
CONFIG_FILE = "config.txt"

# Função para salvar as configurações
def save_config(folder_path, required_level, window_name, check_interval, automation_count, nick):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"PASTA={folder_path}\n")
        f.write(f"LEVEL={required_level}\n")
        f.write(f"JANELA={window_name}\n")
        f.write(f"TEMPO_VERIF={check_interval}\n")
        f.write(f"MR_COUNT={automation_count}\n")
        f.write(f"NICK={nick}\n")

# Função para carregar as configurações
def load_config():
    global automation_count
    config = {"PASTA": "", "LEVEL": "", "JANELA": "", "TEMPO_VERIF": "", "NICK": ""}
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                config[key] = value
            automation_count = int(config.get("MR_COUNT", 0))
    return config["PASTA"], config["LEVEL"], config["JANELA"], config["TEMPO_VERIF"], config["NICK"]

# Função para capturar o Level e Nick do jogo
def capture_area(window_name, offset_left, offset_top, width, height):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        area_left = left + offset_left
        area_top = top + offset_top
        with mss.mss() as sct:
            monitor = {"top": area_top, "left": area_left, "width": width, "height": height}
            screenshot = sct.grab(monitor)
            return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    else:
        print("Janela do jogo não encontrada.")
        return None

def get_text_from_image(image):
    if image:
        gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
        return pytesseract.image_to_string(thresh_image, config='--psm 7').strip()
    return None

def validate_level_and_nick(screenshot_folder, window_name, required_level, required_nick):
    # Captura as imagens da área de level e da área de nick
    level_image = capture_area(window_name, LEVEL_AREA_OFFSET_LEFT, LEVEL_AREA_OFFSET_TOP, LEVEL_AREA_WIDTH, LEVEL_AREA_HEIGHT)
    nick_image = capture_area(window_name, NICK_AREA_OFFSET_LEFT, NICK_AREA_OFFSET_TOP, NICK_AREA_WIDTH, NICK_AREA_HEIGHT)
    
    # Salva a imagem do level
    if level_image:
        level_image.save(os.path.join(screenshot_folder, "level_area_screenshot.jpg"))
        print("Imagem da área do level salva com sucesso.")

    # Salva a imagem do nick
    if nick_image:
        nick_image.save(os.path.join(screenshot_folder, "nick_area_screenshot.jpg"))
        print("Imagem da área do nick salva com sucesso.")
    
    # Realiza o OCR para extrair texto das imagens de level e nick
    level_text = get_text_from_image(level_image)
    nick_text = get_text_from_image(nick_image)
    
    print(f"Level Detectado: {level_text}")
    print(f"Nick Detectado: {nick_text}")
    
    try:
        level = int(''.join(filter(str.isdigit, level_text)))
        if level >= int(required_level) and required_nick in nick_text:
            print("Condições atendidas. Iniciando automação...")
            return True
    except ValueError:
        print("Erro ao detectar o Level.")
    
    return False

# Função principal de automação
def automation_interface_loop(screenshot_folder, required_level, window_name, check_interval, required_nick):
    global automation_running, automation_count, last_level_checked, last_nick_checked
    
    while automation_running:
        if validate_level_and_nick(screenshot_folder, window_name, required_level, required_nick):
            mu_automation.execute_commands()
            automation_count += 1
            save_config(screenshot_folder, required_level, window_name, check_interval, automation_count, required_nick)
            update_count_label()
        else:
            print("Condições não atendidas.")
            countdown(countdown_label, int(check_interval))

# Função para exibir o countdown
def countdown(label, seconds):
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        label.config(text=f"Próxima verificação em: {mins:02}:{secs:02}")
        time.sleep(1)
    label.config(text="Verificando...")

# Função para atualizar o rótulo do contador na interface
def update_count_label():
    count_label.config(text=f"MR Quantidade: {automation_count} | Último Level: {last_level_checked} | Último Nick: {last_nick_checked}")

# Função para iniciar a automação
def start_automation():
    global automation_running
    if not automation_running:
        screenshot_folder = folder_entry.get()
        required_level = int(level_entry.get())
        window_name = window_name_entry.get()
        check_interval = interval_entry.get()
        required_nick = nick_entry.get()

        if not os.path.isdir(screenshot_folder):
            messagebox.showerror("Erro", "Pasta de screenshots inválida.")
            return

        save_config(screenshot_folder, required_level, window_name, check_interval, automation_count, required_nick)
        automation_running = True
        threading.Thread(
            target=automation_interface_loop, 
            args=(screenshot_folder, required_level, window_name, check_interval, required_nick)
        ).start()
    else:
        messagebox.showinfo("Automação", "A automação já está em execução.")

# Função para parar a automação
def stop_automation():
    global automation_running
    automation_running = False
    print("Automação pausada.")

# Interface Gráfica
root = tk.Tk()
root.title("Controle de Automação")
root.geometry("500x600")

# Campos da interface
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

# Carrega configurações salvas
folder, level, window, interval, nick = load_config()
folder_entry.insert(0, folder)
level_entry.insert(0, level)
window_name_entry.insert(0, window)
interval_entry.insert(0, interval)
nick_entry.insert(0, nick)

# Rótulo do contador de Master Resets e nível
count_label = tk.Label(root, text=f"MR Quantidade: {automation_count} | Último Level: {last_level_checked} | Último Nick: {last_nick_checked}")
countdown_label = tk.Label(root, text="Próxima verificação em:")

# Botões de controle
start_button = tk.Button(root, text="Iniciar Automação", command=start_automation, bg="green", fg="white", width=20)
stop_button = tk.Button(root, text="Parar Automação", command=stop_automation, bg="red", fg="white", width=20)

# Texto de rodapé "Desenvolvido por Ed"
footer_label = tk.Label(root, text="Desenvolvido por Ed", font=("Helvetica", 8))
footer_label.place(relx=1.0, rely=1.0, anchor="se")

# Texto de aviso em vermelho
warning_label = tk.Label(root, text="AVISO: O inventário do personagem é limpo a cada MR.", font=("Helvetica", 8), fg="red")

# Disposição na interface
for widget in [
    folder_label, folder_entry, folder_button,
    level_label, level_entry, window_name_label, window_name_entry,
    interval_label, interval_entry, nick_label, nick_entry,
    count_label, countdown_label, start_button, stop_button,
    warning_label  # Adiciona o aviso em vermelho ao final
]:
    widget.pack(pady=5)

# Iniciar loop da interface
root.mainloop()
