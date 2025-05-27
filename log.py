import json  # Manipula dados em formato JSON.
import logging  # Cria e gerencia logs de execução.
import time  # Manipula tempo e adiciona atrasos.
import os  # Interage com o sistema operacional (arquivos, diretórios).

# Criando diretório único para cada execução "logs/{DATA_HORA}"
log_dir = os.path.join(os.getcwd(),r"\logs", time.strftime("%Y-%m-%d_%H-%M-%S"))
os.makedirs(log_dir, exist_ok=True)

# Configuração do logging
logging.basicConfig(
    filename= os.path.join(log_dir, "log.log"),
    level=logging.INFO,  # Captura TODOS os níveis menos o nivel debug de log
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding='utf-8' # Define a codificação do arquivo de log para utf-8
)

# Arquivo JSON para armazenar logs
log_json_file = os.path.join(log_dir, "log.json")

# Lista de logs para salvar no JSON
logs = {
    "data_execucao": time.strftime("%Y-%m-%d %H:%M"),
    "resultado": None,  # Será preenchido no final
    "registros": []
}

def register_log(level, message, screenshot_path=None):
    print(level, message, screenshot_path)
    # Registra logs no JSON e no arquivo .log

    # Estrutura do log
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": level.upper(),
        "message": message
    }

    # Adiona a url da imagem da estrura
    if screenshot_path:
        log_entry["screenshot"] = screenshot_path

    # Registra o log no JSON
    logs["registros"].append(log_entry)
    with open(log_json_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

    # Registra o log no .log
    match level.lower():
        case "debug": #10 - Valor do Nivel
            logging.debug(message)
        case "info": #20 - Valor do Nivel
            logging.info(message)
        case "warning": #30 - Valor do Nivel
            logs["resultado"] = "FALHA"
            logging.warning(message)
        case "error": #40 - Valor do Nivel
            logging.error(message)
        case "critical": #50 - Valor do Nivel
            logging.critical(message)
        case "sucesso": #Valor personalizado Define o status do processo
            logs["resultado"] = level.upper()
            logging.info(message)
        case _:
            raise ValueError("Nivel não identificado")

# Função para capturar screenshot em caso de erro
def captura_screenshot(navegador, level, message):
    """Captura um screenshot e registra no log"""
    screenshot_path = os.path.join(log_dir, f"{time.strftime('%H-%M-%S')}.png")
    
    try:
        navegador.save_screenshot(screenshot_path)
        register_log(level, message, screenshot_path)
    except Exception as e:
        register_log("error", f"Erro ao capturar screenshot: {e}")