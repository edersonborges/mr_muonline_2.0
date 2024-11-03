# mu_automation.py
# -*- coding: utf-8 -*-
import pyautogui
import time
import win32gui
import win32con
import ctypes

# Nome da janela do jogo
GAME_WINDOW_NAME = "CristalMU 97D"

# Lista de comandos
COMMANDS = [
    "/zen 9999999999",
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

# Função para focar a janela do jogo
def focus_game_window():
    hwnd = win32gui.FindWindow(None, GAME_WINDOW_NAME)
    if hwnd:
        if not is_window_in_focus(hwnd):
            ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            time.sleep(0.1)
            ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_RESTORE)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            time.sleep(0.5)
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
        if focus_game_window():
            print(f"Enviando comando: {command}")
            pyautogui.keyDown('enter')
            pyautogui.keyUp('enter')
            pyautogui.write(command)
            pyautogui.keyDown('enter')
            pyautogui.keyUp('enter')
            time.sleep(1)
        else:
            print("Falha ao focar a janela. Tentando novamente...")
