# -*- coding: utf-8 -*-
import pyautogui
import time
import win32gui
import win32con
import ctypes
import keyboard

# Nome da janela do jogo
GAME_WINDOW_NAME = "CristalMU 97D"

# Lista de comandos
COMMANDS = [
    "/mreset",
    "/f 32767",
    "/a 32767",
    "/e 32767",
    "/v 32767",
    "/limparinv"
]

# Função para verificar se a janela está em foco
def is_window_in_focus(hwnd):
    foreground_hwnd = win32gui.GetForegroundWindow()
    return hwnd == foreground_hwnd  # Retorna True se a janela do jogo está em foco

def focus_game_window():
    hwnd = win32gui.FindWindow(None, GAME_WINDOW_NAME)
    if hwnd:
        if not is_window_in_focus(hwnd):  # Verifica se a janela já está em foco
            ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_MINIMIZE)  # Minimiza a janela
            time.sleep(0.1)  # Pequeno atraso para garantir que a ação de minimizar foi processada
            ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restaura a janela
            ctypes.windll.user32.SetForegroundWindow(hwnd)  # Tentar focar a janela
            time.sleep(0.5)  # Aguardar meio segundo para garantir o foco
        # Verifica novamente se a janela está em foco
        if is_window_in_focus(hwnd):
            print("Janela do jogo está em foco.")
            return True
        else:
            print("Falha ao trazer a janela para o foco.")
            return False
    else:
        print("Janela do jogo não encontrada.")
        return False


# Função para enviar os comandos
def execute_commands():
    for command in COMMANDS:
        if focus_game_window():  # Garante o foco antes de cada comando
            print(f"Enviando comando: {command}")
            pyautogui.keyDown('enter')
            pyautogui.keyUp('enter')  # Abrir o chat
            pyautogui.write(command)
            pyautogui.keyDown('enter')
            pyautogui.keyUp('enter')  # Executar o comando
            time.sleep(1)  # Atraso de 1 segundo entre os comandos para garantir o processamento
        else:
            print("Falha ao focar a janela. Tentando novamente...")

# Função para contagem regressiva
def countdown(seconds, message="Iniciando nova execução em"):
    while seconds > 0 and not keyboard.is_pressed("2"):  # Interrompe a contagem se a tecla '2' for pressionada
        mins, secs = divmod(seconds, 60)
        timer = f"{mins:02}:{secs:02}"
        print(f"{message} {timer}", end="\r")  # Imprime na mesma linha
        time.sleep(1)
        seconds -= 1
    print("\nIniciando nova execução...")

# Função principal para gerenciar a automação
def automation_loop():
    running = False
    print("Pressione '1' para iniciar e '2' para parar a automação.")

    while True:
        if keyboard.is_pressed("1") and not running:  # Inicia a automação ao pressionar '1'
            running = True
            print("Iniciando contagem regressiva de 10 segundos para começar a automação...")
            countdown(10, message="Automação começando em")  # Contagem regressiva de 10 segundos para iniciar

        if running:
            # Tentar focar a janela até 10 vezes
            focus_attempts = 0
            while focus_attempts < 10:
                if focus_game_window():  # Se a janela foi focada com sucesso
                    print("Janela focada com sucesso, iniciando automação...")
                    execute_commands()   # Executar os comandos
                    break
                else:
                    print(f"Tentativa {focus_attempts + 1} de 10 para focar a janela...")
                    focus_attempts += 1
                    time.sleep(1)  # Aguardar 1 segundo entre as tentativas

            # Se a janela não foi focada após 10 tentativas
            if focus_attempts == 10:
                print("Falha ao focar a janela após 10 tentativas. Verifique se o jogo está aberto.")

            # Contagem regressiva de 30 segundos antes de repetir o ciclo
            countdown(30)  # Altere o valor aqui para definir o intervalo desejado entre execuções

        if keyboard.is_pressed("2"):  # Interrompe a automação ao pressionar '2'
            print("Automação pausada.")
            running = False
            break

# Iniciar o loop de automação
automation_loop()
