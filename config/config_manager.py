import os

CONFIG_FILE = "config.txt"

def save_config(folder_path, required_level, window_name, check_interval, automation_count, nick):
    """Salva as configurações em um arquivo de texto."""
    with open(CONFIG_FILE, "w") as f:
        f.write(f"PASTA={folder_path}\n")
        f.write(f"LEVEL={required_level}\n")
        f.write(f"JANELA={window_name}\n")
        f.write(f"TEMPO_VERIF={check_interval}\n")
        f.write(f"MR_COUNT={automation_count}\n")
        f.write(f"NICK={nick}\n")

def load_config():
    """Carrega as configurações de um arquivo de texto."""
    config = {"PASTA": "", "LEVEL": "", "JANELA": "", "TEMPO_VERIF": "", "NICK": ""}
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                config[key] = value
            automation_count = int(config.get("MR_COUNT", 0))
            return config["PASTA"], config["LEVEL"], config["JANELA"], config["TEMPO_VERIF"], config["NICK"], automation_count
    return "", "", "", "", "", 0
