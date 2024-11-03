import mss
from PIL import Image

# Defina as coordenadas da área do level conforme identificado
LEVEL_AREA_OFFSET_LEFT = 620    # Coordenada X do canto superior esquerdo do Level
LEVEL_AREA_OFFSET_TOP = 160     # Coordenada Y do canto superior esquerdo do Level
LEVEL_AREA_WIDTH = 100          # Largura da área do Level
LEVEL_AREA_HEIGHT = 30          # Altura da área do Level

def capture_level_area():
    with mss.mss() as sct:
        monitor = {
            "top": LEVEL_AREA_OFFSET_TOP,
            "left": LEVEL_AREA_OFFSET_LEFT,
            "width": LEVEL_AREA_WIDTH,
            "height": LEVEL_AREA_HEIGHT
        }
        screenshot = sct.grab(monitor)
        screenshot_image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        screenshot_image.show()  # Exibe a imagem para verificar se está capturando corretamente

# Chame a função para testar a captura da área
capture_level_area()
