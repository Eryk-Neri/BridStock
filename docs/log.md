# Documentação do Módulo de Logs

## Introdução

O módulo `log.py` é responsável pelo registro e monitoramento das atividades do sistema. Ele gera logs tanto em formato estruturado (`log.json`) quanto em texto simples (`log.log`), permitindo rastrear execuções, erros e eventos relevantes.

## `log.json` (Formato Estruturado)
Este arquivo registra os eventos de execução do sistema em um formato JSON, facilitando a análise programática.

```json
{
    "data_execucao": "2025-02-17 10:25",
    "resultado": "SUCESSO" | "FALHA",
    "registros": [
        {
            "timestamp": "2025-02-17 10:25:38",
            "type": "INFO",
            "message": "Atualização Iniciada."
        },
        {...}
    ]
}
```

## `log.log` (Formato Texto)
Este arquivo armazena os registros de log em um formato legível para humanos.

```
AAAA-MM-DD HH:MM:SS - NIVEL - MENSAGEM

2025-02-17 10:25:39 - INFO - Atualização Iniciada.
2025-02-17 10:26:09 - ERROR - Erro capturado: message: javascript error:  
2025-02-17 10:27:49 - WARNING - Erro capturado: Erro ao tentar
...
```

## Níveis de Log
Os registros podem conter os seguintes níveis:
- **INFO**: Informações gerais sobre o andamento da execução.
- **WARNING**: Avisos sobre possíveis problemas que não interrompem a execução.
- **ERROR**: Erros que afetam a execução, mas não causam a parada total do sistema.
- **CRITICAL**: Falhas graves que impedem a continuidade do processo.

## Uso
Para registrar eventos no log, utilize a função `register_log`;
Para registrar um erro no navegador, utilize a função `captura_screenshot`:
```python
from log import *

register_log("info", "Processo iniciado com sucesso.")
captura_screenshot(driver,"warning", "Falha ao acessar a base de dados.")
```

Isso garantirá que os eventos sejam armazenados tanto no `log.json` quanto no `log.log`, mantendo um histórico organizado para auditoria e depuração.

## Codigo `log.py`
O arquivo log.py é responsável por gerenciar o registro de logs do sistema. gerando diretorio, arquivos .json e .log

---

## `imports:`

```python
import json  # Manipula dados em formato JSON.
import logging  # Cria e gerencia logs de execução.
import time  # Manipula tempo e adiciona atrasos.
import os  # Interage com o sistema operacional (arquivos, diretórios).
```

## Configuração
- `.log`
    - Cria diretório único com a data da execução para os registro de erros, se não existir  
        ```python
        log_dir = os.path.join(os.getcwd(),r"\logs", time.strftime("%Y-%m-%d_%H-%M-%S"))
        os.makedirs(log_dir, exist_ok=True)
        ```
    - Faz a formatação para o arquivo .log com a blibioteca logging <br>
        ```python
        logging.basicConfig(
            filename= os.path.join(log_dir, "log.log"),
            level=logging.INFO,  # Captura TODOS os níveis menos o nivel debug de log
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding='utf-8'  # Define a codificação do arquivo de log para utf-8
        )
        ```
        - Parâmetros:
            | Parâmetro | Tipo       | Descrição                                         |
            |-----------|------------|---------------------------------------------------|
            | filename  | dir        | Diretorio para salvar os logs.                    |
            | level     | param      | Apartir de que nivel seja salvo as informações.   |
            | format    | str        | Formatação de ordem das informações no log.       |
            | datefmt   | data hora  | Formatação de como vai ser apresentada as datas.  |
            | encoding  | str        | especifica a codificação de caracteres especiais. |

    - Cria arquivo JSON dentro do diretorio
        ```python
        log_json_file = os.path.join(log_dir, "log.json")
        ```

    - Faz a estrutura base do arquivo JSON
        ```python
        # Lista de logs para salvar no JSON
        logs = {
            "data_execucao": time.strftime("%Y-%m-%d %H:%M"),
            "resultado": None,  # Será preenchido no final
            "registros": []
        }
        ```

## Funções

## `register_log()`
Registra logs em um arquivo JSON e em um arquivo `.log`, permitindo o acompanhamento de mensagens de depuração, informações, alertas, erros e sucessos.

### **Fluxo da função:**
1. **Cria a estrutura do log com timestamp e nível da mensagem.**  
```python
# Estrutura do log
log_entry = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "type": level.upper(),
    "message": message
}
```

2. **Adiciona o caminho do screenshot, caso exista.**  
```python
 # Adiona a url da imagem da estrura
if screenshot_path:
      log_entry["screenshot"] = screenshot_path
```

3. **Registra o log no arquivo JSON.**  
```python
# Registra o log no JSON
    logs["registros"].append(log_entry)
    with open(log_json_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)
```

4. **Registra o log no arquivo `.log`, categorizando pelo nível de severidade.**  
```python
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
```

### **Parâmetros:**
| Parâmetro        | Tipo      | Descrição                                            |
|------------------|----------|------------------------------------------------------|
| `level`         | `str`    | Nível do log (`debug`, `info`, `warning`, `error`, `critical`, `sucesso`). |
| `message`       | `str`    | Mensagem do log.                                     |
| `screenshot_path` | `str` ou `None` | Caminho opcional para uma captura de tela relacionada ao log. |

### **Retorno:**
- Nenhum retorno. A função grava logs nos arquivos especificados.

### **Erros Tratados:**
- Caso o nível do log não seja reconhecido, um erro é levantado.
```python
raise ValueError("Nivel não identificado")
```

---

## `Função: captura_screenshot()`

Captura uma screenshot da tela do navegador em caso de erro e registra no log.

### **Fluxo da função:**
1. **Cria o nome do arquivo de screenshot com timestamp.**  
```python
"""Captura um screenshot e registra no log"""
screenshot_path = os.path.join(log_dir, f"{time.strftime('%H-%M-%S')}.png")
```

2. **Define o caminho de salvamento e captura a imagem.**  
```python
try:
      navegador.save_screenshot(screenshot_path)
```

3. **Registra o log com o caminho do screenshot.**  
```python
      register_log(level, message, screenshot_path)
```

### **Parâmetros:**
| Parâmetro  | Tipo        | Descrição                                  |
|------------|------------|--------------------------------------------|
| `navegador` | `WebDriver` | Instância do Selenium WebDriver.         |
| `level`     | `str`      | Nível do log (`error`, `warning`, etc.). |
| `message`   | `str`      | Mensagem associada ao log.               |

### **Retorno:**
- Nenhum retorno. A função apenas captura a tela e registra o log.

### **Erros Tratados:**
- Caso o nível do log não seja reconhecido, um erro é levantado.
```python
except Exception as e:
      register_log("error", f"Erro ao capturar screenshot: {e}")
```