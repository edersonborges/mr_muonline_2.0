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

# Configurações de área do level
LEVEL_AREA_OFFSET_LEFT = 550    # Coordenada X do canto superior esquerdo do Level
LEVEL_AREA_OFFSET_TOP = 90      # Coordenada Y do canto superior esquerdo do Level
LEVEL_AREA_WIDTH = 150          # Largura da área do Level
LEVEL_AREA_HEIGHT = 30          # Altura da área do Level

# Caminho do arquivo de configuração
CONFIG_FILE = "config.txt"

# Função para salvar as configurações
def save_config(folder_path, required_level, window_name, check_interval, automation_count):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"{folder_path}\n{required_level}\n{window_name}\n{check_interval}\n{automation_count}")

# Função para carregar as configurações
def load_config():
    global automation_count
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 5:
                folder_path = lines[0].strip()
                required_level = lines[1].strip()
                window_name = lines[2].strip()
                check_interval = lines[3].strip()
                automation_count = int(lines[4].strip())  # Carrega o contador de MR
                return folder_path, required_level, window_name, check_interval
    return "", "", "", ""  # Retorna valores vazios se o arquivo não existir ou estiver incompleto

# Função para pressionar a tecla "C" usando win32api
def press_key_c():
    win32api.keybd_event(0x43, 0, 0, 0)  # Pressiona a tecla C (código de tecla 0x43)
    time.sleep(0.1)
    win32api.keybd_event(0x43, 0, win32con.KEYEVENTF_KEYUP, 0)  # Solta a tecla C

# Função para capturar a área específica do Level da janela do jogo
def get_level_from_screenshot(screenshot_folder, window_name):
    hwnd = win32gui.FindWindow(None, window_name)  # Nome da janela do jogo
    if hwnd:
        # Obtenha as coordenadas da janela do jogo
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        
        # Calcula a posição da área do level baseada na posição da janela
        level_left = left + LEVEL_AREA_OFFSET_LEFT
        level_top = top + LEVEL_AREA_OFFSET_TOP
        level_right = level_left + LEVEL_AREA_WIDTH
        level_bottom = level_top + LEVEL_AREA_HEIGHT

        # Usa mss para capturar a região do Level
        with mss.mss() as sct:
            monitor = {"top": level_top, "left": level_left, "width": LEVEL_AREA_WIDTH, "height": LEVEL_AREA_HEIGHT}
            screenshot = sct.grab(monitor)
            screenshot_image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Salvar a imagem da área do Level para verificação
            screenshot_path = os.path.join(screenshot_folder, "level_area_screenshot.jpg")
            screenshot_image.save(screenshot_path)
            print(f"Screenshot da área do level salva em: {screenshot_path}")
            
            # Converte a imagem para escala de cinza e aplica um threshold para melhorar o OCR
            gray_image = cv2.cvtColor(np.array(screenshot_image), cv2.COLOR_BGR2GRAY)
            _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

            # Usa OCR para extrair o texto do level
            level_text = pytesseract.image_to_string(thresh_image, config='--psm 7')
            print(f"Texto capturado: {level_text}")
            
            # Extrai apenas o número do level
            try:
                level = int(''.join(filter(str.isdigit, level_text.split("Level:")[-1].strip())))
                print(f"Nível detectado: {level}")
                return level
            except ValueError:
                print("Nível não detectado na imagem.")
                # Se o nível não for encontrado, tenta focar a janela e pressionar "C"
                if mu_automation.focus_game_window():
                    print("Focando na janela e pressionando 'C' para abrir o status.")
                    press_key_c()
                    time.sleep(1)
                return None
    else:
        print("Janela do jogo não encontrada.")
        return None

# Função principal de automação baseada no level
def automation_interface_loop(screenshot_folder, required_level, window_name, check_interval):
    global automation_running, automation_count, last_level_checked
    check_interval = int(check_interval)

    while automation_running:
        # Foca na janela do jogo antes de capturar a tela
        if not mu_automation.focus_game_window():
            print("Falha ao focar a janela do jogo. Tentando novamente em 5 segundos.")
            time.sleep(5)
            continue  # Tenta novamente se o foco falhar

        # Obter o level da screenshot mais recente
        level = get_level_from_screenshot(screenshot_folder, window_name)
        
        # Atualiza o último nível verificado e o exibe na interface
        last_level_checked = level if level is not None else "Não detectado"
        update_count_label()  # Atualiza o rótulo na interface com o nível atual

        # Verifica se o level atende à condição necessária (maior ou igual ao nível requerido)
        if level is not None and level >= required_level:
            print("Nível necessário atingido! Iniciando automação...")
            mu_automation.execute_commands()
            automation_count += 1  # Incrementa o contador de Master Resets
            update_count_label()  # Atualiza o rótulo na interface
            print(f"Contador de MR: {automation_count}")
            save_config(screenshot_folder, required_level, window_name, check_interval, automation_count)  # Salva o contador atualizado
        else:
            print(f"Nível {level} não atingido. Verificando novamente em {check_interval} segundos.")
            # Exibe o countdown no rótulo de tempo restante
            countdown(countdown_label, check_interval)
            
# Função para exibir o countdown
def countdown(label, seconds):
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        label.config(text=f"Próxima verificação em: {mins:02}:{secs:02}")
        time.sleep(1)
    label.config(text="Verificando...")

# Função para atualizar o rótulo do contador na interface
def update_count_label():
    count_label.config(text=f"MR Quantidade: {automation_count} | Último Level: {last_level_checked}")

# Função para iniciar a automação
def start_automation():
    global automation_running
    if not automation_running:
        # Pega os valores do formulário
        screenshot_folder = folder_entry.get()
        required_level = int(level_entry.get())
        window_name = window_name_entry.get()
        check_interval = interval_entry.get()
        
        if not os.path.isdir(screenshot_folder):
            messagebox.showerror("Erro", "Pasta de screenshots inválida.")
            return

        # Salva as configurações atuais
        save_config(screenshot_folder, required_level, window_name, check_interval, automation_count)

        # Bloqueia os campos de entrada e muda a cor para cinza
        folder_entry.config(state='disabled', bg='light gray')
        level_entry.config(state='disabled', bg='light gray')
        window_name_entry.config(state='disabled', bg='light gray')
        interval_entry.config(state='disabled', bg='light gray')

        automation_running = True
        automation_thread = threading.Thread(
            target=automation_interface_loop, 
            args=(screenshot_folder, required_level, window_name, check_interval)
        )
        automation_thread.daemon = True
        automation_thread.start()
    else:
        messagebox.showinfo("Automação", "A automação já está em execução.")

# Função para parar a automação
def stop_automation():
    global automation_running
    automation_running = False
    print("Automação pausada.")
    
    # Desbloqueia os campos de entrada e restaura a cor padrão
    folder_entry.config(state='normal', bg='white')
    level_entry.config(state='normal', bg='white')
    window_name_entry.config(state='normal', bg='white')
    interval_entry.config(state='normal', bg='white')
    countdown_label.config(text="Automação pausada.")

# Função para selecionar a pasta de screenshots
def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_selected)

# Interface Gráfica
root = tk.Tk()
root.title("Controle de Automação")
root.geometry("450x500")

# Seção para selecionar a pasta de screenshots
folder_label = tk.Label(root, text="Pasta de Screenshots:")
folder_label.pack(pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.pack(pady=5)
folder_button = tk.Button(root, text="Selecionar Pasta", command=select_folder)
folder_button.pack(pady=5)

# Campo para o level necessário
level_label = tk.Label(root, text="Level Necessário:")
level_label.pack(pady=5)
level_entry = tk.Entry(root, width=5)
level_entry.pack(pady=5)

# Campo para o nome da janela do jogo
window_name_label = tk.Label(root, text="Nome da Janela do Jogo:")
window_name_label.pack(pady=5)
window_name_entry = tk.Entry(root, width=20)
window_name_entry.pack(pady=5)

# Campo para o intervalo de verificação
interval_label = tk.Label(root, text="Intervalo de Verificação (segundos):")
interval_label.pack(pady=5)
interval_entry = tk.Entry(root, width=5)
interval_entry.pack(pady=5)

# Carrega configurações salvas
last_folder, last_level, last_window_name, last_interval = load_config()
folder_entry.insert(0, last_folder)
level_entry.insert(0, last_level)
window_name_entry.insert(0, last_window_name)
interval_entry.insert(0, last_interval)

# Rótulo do contador de Master Resets e nível
count_label = tk.Label(root, text=f"MR Quantidade: {automation_count} | Último Level: {last_level_checked}", font=("Helvetica", 12))
count_label.pack(pady=10)

# Rótulo do countdown
countdown_label = tk.Label(root, text="Próxima verificação em:", font=("Helvetica", 10))
countdown_label.pack(pady=5)

# Botões de controle
start_button = tk.Button(root, text="Iniciar Automação", command=start_automation, bg="green", fg="white", width=20)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Parar Automação", command=stop_automation, bg="red", fg="white", width=20)
stop_button.pack(pady=10)

# Exibe a logo, se disponível
logo_path = "logo.png" if os.path.exists("logo.png") else "logo.jpg"
if os.path.exists(logo_path):
    logo_image = Image.open(logo_path)
    logo_image = logo_image.resize((100, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo)
    logo_label.pack(side="bottom", pady=5)

# Texto de rodapé
footer_label = tk.Label(root, text="Desenvolvido por Ed", font=("Helvetica", 8))
footer_label.place(relx=1.0, rely=1.0, anchor="se")

# Iniciar o loop da interface
root.mainloop()