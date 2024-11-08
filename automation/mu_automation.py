# automation/mu_automation.py
import time
import win32gui
import win32con
import pyautogui

COMMANDS = [
    "/zen 9999999999",
    "/mreset",
    "/f 32767",
    "/a 32767",
    "/e 32767",
    "/v 32767",
    "/limparinv"
]

def focus_game_window(window_name):
    """Tenta focar a janela do jogo pelo nome."""
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    else:
        print(f"Janela com nome '{window_name}' não encontrada.")
        return False

def execute_commands(window_name):
    """Executa os comandos na janela do jogo."""
    if focus_game_window(window_name):
        for command in COMMANDS:
            print(f"Enviando comando: {command}")
            pyautogui.keyDown('enter')
            pyautogui.keyUp('enter')
            pyautogui.write(command)
            pyautogui.keyDown('enter')
            pyautogui.keyUp('enter')
            time.sleep(1)
    else:
        print("Não foi possível focar na janela do jogo.")
