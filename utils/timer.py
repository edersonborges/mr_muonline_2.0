import time

def countdown(label, seconds):
    """Exibe uma contagem regressiva em um rótulo de interface."""
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        label.config(text=f"Próxima verificação em: {mins:02}:{secs:02}")
        time.sleep(1)
    label.config(text="Verificando...")
