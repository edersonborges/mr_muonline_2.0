import mss
from PIL import Image
import cv2
import numpy as np
import pytesseract
import win32gui  # Adicione esta linha para importar win32gui

# Certifique-se de definir o caminho do Tesseract corretamente no arquivo principal (interface.py ou image_processing.py)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def capture_area(window_name, offset_left, offset_top, width, height):
    """Captura uma área específica da janela do jogo."""
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
    """Realiza OCR para extrair texto de uma imagem."""
    if image:
        gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
        return pytesseract.image_to_string(thresh_image, config='--psm 7').strip()
    return None
