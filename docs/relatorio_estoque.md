# Documentação do Script `relatorio_estoque.py`

## Introdução

O script `relatorio_estoque.py` é o módulo principal do sistema de automação de controle de estoque. Ele executa todas as etapas do processo, desde a extração de dados no ERP Sankhya até a atualização dos estoques das lojas da Empresa1 e Empresa2 na plataforma Tray.

## Fluxo de Execução

1. **Registro de Início**: O sistema inicia e registra a execução nos logs.
2. **Configuração do Navegador**: O navegador é configurado para execução automatizada.
3. **Login no Sankhya**: Autentica-se no ERP para acessar os dados.
4. **Extração de Estoque**: Acessa o painel "Estoque Reservado" e exporta os dados.
5. **Verificação de Download**: Aguarda a conclusão do download do arquivo de estoque.
6. **Processamento do Arquivo**: Renomeia e organiza os dados do estoque.
7. **Filtragem e Segmentação**: Separa os estoques das lojas da Empresa1 e Empresa2.
8. **Atualização do Estoque**: Realiza o upload dos dados processados para as lojas na Tray.
9. **Registro de Conclusão**: Finaliza o processo e encerra o navegador.

## Estrutura do Código

### Funções Principais

- `config_browser(diretorio, visualizar, baixar_arquivos)`
  - Configura o navegador para execução automatizada.

- `login_sankhya(driver)`
  - Realiza o login no ERP Sankhya.

- `pesquisar_estoque(driver)`
  - Navega até o painel de "Estoque Reservado".

- `exportar_tabela(driver)`
  - Exporta os dados de estoque do ERP.

- `verifica_download(diretorio)`
  - Aguarda a finalização do download do arquivo.

- `organiza_arquivo(diretorio)`
  - Renomeia e armazena o arquivo exportado.

- `filtra_separa_estoque(arquivo)`
  - Separa os dados de estoque entre Empresa1 e Empresa2.

- `update_estoque_Empresa2(arquivo, driver)`
  - Atualiza o estoque da loja Empresa2 na Tray.

- `update_estoque_Empresa1(arquivo, driver)`
  - Atualiza o estoque da loja Empresa1 na Tray.

- `register_log(nivel, mensagem)`
  - Registra eventos no sistema de logs.

- `captura_screenshot(driver, nivel, mensagem)`
  - Captura uma tela em caso de erro.

## Execução do Script

Para rodar o script manualmente:
```sh
python relatorio_estoque.py
```

Isso iniciará todo o fluxo de automação descrito acima.

## Tratamento de Erros

O script conta com captura de exceções para evitar falhas críticas, incluindo:
- Erros de login no Sankhya.
- Problemas no download de arquivos.
- Falhas na importação de estoque para as lojas.

Em caso de erro, uma captura de tela é gerada e um log é salvo para posterior análise.

---
Essa documentação fornece uma visão geral do funcionamento do `relatorio_estoque.py`. Caso precise de detalhes adicionais, consulte o código-fonte.

## Codigo `relatorio_estoque.py`

O arquivo `relatorio_estoque.py` tem como objetivo realizar a atualização de estoque das lojas **Empresa1** e **Empresa2** através da plataforma Tray. Ele automatiza o login, acessa a ferramenta de importação de dados e carrega arquivos Excel contendo as informações de estoque.

---

## `imports:`

```python
from selenium import webdriver  # Para automação de navegação no navegador
from selenium.webdriver.edge.service import Service as EdgeService  # Para gerenciar o serviço do Edge
from selenium.webdriver.common.by import By  # Para localizar elementos na página
from selenium.webdriver.common.keys import Keys  # Para simular pressionamento de teclas
from webdriver_manager.microsoft import EdgeChromiumDriverManager  # Para gerenciar o driver do Edge
from selenium.webdriver.support.ui import WebDriverWait  # Para aguardar condições na página
from selenium.webdriver.support import expected_conditions as EC  # Para condições esperadas na página
from urllib.parse import urlparse  # Para manipulação e análise de URLs
from datetime import date  # Para manipulação de datas
from datetime import datetime  # Para manipulação de datas e horas
from log import *  # Para manipulação de logs
import glob  # Para buscar arquivos com padrões específicos
import time  # Para gerenciar tempos de espera e pausas
import pandas as pd  # Para manipulação de dados em tabelas
import os  # Para interação com o sistema operacional (arquivos, diretórios, etc.)
```
---

## `Função: config_browser()`

Configura o navegador Microsoft Edge para automação com Selenium.

### **Fluxo da função:**
1. **Define o diretório de download**
   - Cria a pasta de destino caso não exista.
   ```python
    pasta_download = os.path.join(os.getcwd(), diretorio)
    os.makedirs(pasta_download, exist_ok=True) # Criar pasta se não existir
   ```
   
2. **Adiciona argumentos no navegador**
    ```python
    edge_options = webdriver.EdgeOptions()

    edge_options.add_argument("--disable-gpu")  # Melhor compatibilidade com alguns sistemas
    edge_options.add_argument("--window-size=1920x1080")  # Define tamanho da janela
    edge_options.add_argument("--disable-notifications")  # Bloqueia notificações
    edge_options.add_argument("--no-sandbox")  # Evita problemas de permissão (Linux)
    edge_options.add_argument("--disable-dev-shm-usage")  # Melhor uso de memória em sistemas Linux
    edge_options.add_argument("--disable-blink-features=AutomationControlled")  # Tenta evitar detecção de bots
    edge_options.add_argument("--start-maximized")  # Inicia com tela cheia
    edge_options.add_argument("--log-level=3")  # Reduz mensagens de log
    edge_options.add_argument("--disable-blink-features=AutomationControlled")  # Oculta automação
    edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Permitir cookies
    edge_options.add_argument("--enable-cookies")
    edge_options.add_argument("--disable-popup-blocking")
    ```
   - Mantem o navegador aberto após o script terminar
   ```python
   if debug:
        #Se quiser manter o navegador aberto mesmo após o script terminar
        edge_options.add_experimental_option("detach", True)
  ```
   - Define argumentos para execução headless (com ou sem interface gráfica).
   ```python
   if not headless:
        edge_options.add_argument("--headless")  # Rodar sem interface gráfica (remova se quiser ver a UI)
    ```
3. **Adiciona as preferencias no navegador**
    ```python
     prefs = {
        "download.default_directory": pasta_download,  # Definir a pasta de download
        "download.prompt_for_download": False,  # Impede o navegador de perguntar onde salvar
        "download.directory_upgrade": True,  # Substitui a pasta de download padrão
        "safebrowsing.enabled": True,  # Desativa a verificação de segurança no download
        "safebrowsing.disable_download_protection": True,  # Desativa a proteção contra downloads "inseguros"
        "profile.default_content_settings.popups": 0,  # Bloqueia pop-ups
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        "excludeSwitches": ["enable-automation"], # Remove a flag de automação
        "useAutomationExtension": False # Desativa extensões de automação
    }
    edge_options.add_experimental_option("prefs", prefs)
    ```
4. **Retorna a instância do navegador configurada**
  ```python
  return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=edge_options)
  ```

### **Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `diretorio` | `str` | Caminho do diretório de downloads. |
| `headless` | `bool` | Define se o navegador será executado sem interface gráfica. |
| `debug` | `bool` | Define se o navegador será mantido aberto após a execução. |

### **Retorno:**
- Retorna uma instância do `webdriver.Edge()` com as configurações aplicadas.

---
## `Função: login_sankhya()`

Realiza o login no sistema Sankhya através da interface web.

### **Fluxo da função:**
1. **Acessa a página do Sankhya**
   - Abre a URL de login no navegador.
   - Maximiza a janela.
   - Aguarda o carregamento.
   ```python
   navegador.get("")
    navegador.fullscreen_window()
    time.sleep(5)
    ```
   
2. **Interage com o Shadow DOM**
   - Localiza o componente `<sankhya-login>`.
   ```python
   # Acessar o Shadow DOM dentro do Web Component <sankhya-login>
    shadow_root = navegador.execute_script("return arguments[0].shadowRoot", navegador.find_element(By.TAG_NAME, "sankhya-login"))
    ```
   - Insere usuário e senha.
   ```python
   #Inserção do Usuario
    user_input = shadow_root.find_element(By.ID, "user")  #pega o input para inserir usuario
    user_input.send_keys("") #Insere usuario 
    user_input.send_keys(Keys.RETURN) #preciona Enter
    ```
   - Confirma login pressionando Enter.
   ```python
   #Inserção do Senha
    user_input = shadow_root.find_element(By.ID, "password")  #pega o input para inserir a Senha
    user_input.send_keys("") #Insere Senha
    user_input.send_keys(Keys.RETURN) #preciona Enter
   ```
   
3. **Aguarda o carregamento completo**
   - O login pode levar alguns segundos, então há um tempo de espera para garantir o acesso.
   ```python
   time.sleep(20)
   ```

### **Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `navegador` | `webdriver` | Instância do navegador Selenium. |

### **Retorno:**
- Não retorna valores, apenas realiza a autenticação na plataforma.

---

## `Função: pesquisar_estoque()`

Realiza a pesquisa de "ESTOQUE RESERVADO" no sistema.

### **Fluxo da função:**
1. **Aguarda o campo de pesquisa estar disponível.**
```python
try:
        # Espera até que o campo de pesquisa esteja visível e interativo
        search_input = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.ID, "search-input-element"))
        )
```
2. **Digita "ESTOQUE RESERVADO" no campo de pesquisa.**
```python
        search_input.send_keys("ESTOQUE RESERVADO") # Digita "ESTOQUE RESERVADO"
        time.sleep(2)  
```
3. **Pressiona Enter para executar a busca.**
```python
        search_input.send_keys(Keys.RETURN) # Pressiona ENTER para pesquisar  
```
4. **Registra no log que a pesquisa foi realizada com sucesso.**
```python
        register_log("info","Pesquisa realizada com sucesso!")
```

### **Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `navegador` | `webdriver` | Instância do navegador Selenium. |

### **Retorno:**
- Nenhum. Apenas realiza a pesquisa no sistema.

### **Erros Tratados:**
- Caso ocorra um erro durante a pesquisa, a exceção é propagada para ser tratada na `main()`.
```python
except Exception as e:
        raise ValueError(f"Erro ao pesquisar: {e}") # Propaga o erro para o main()
```
---
## `Função: exportar_tabela()`

Exporta a tabela de estoque para um arquivo Excel e envia por e-mail.

### **Fluxo da função:**
1. **Define um tempo maximo para esperar o elemento**
```python
wait = WebDriverWait(navegador, 20)  # Tempo máximo de espera de 20 segundos
```
2. **Acessa o iframe.**
```python
try:
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "gwt-Frame")))
        register_log("info","Mudou para o iframe!")
```
3. **Clica no botão de exportação.**
```python
        # ** Clicar no botão de exportação principal**
        botao_exportar = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "sk-grid-printer button.btn-default.dropdown-toggle"))
        )
        botao_exportar.click()
        register_log("info","Botão de exportação clicado!")
```
4. **Seleciona a opção de exportação para Excel.**
```python
        # ** Aguardar a popover aparecer**
        wait.until(EC.visibility_of_element_located((By.ID, "sk-popover-002")))
        time.sleep(1)  # Pequena pausa para garantir a renderização

        # ** Clicar na opção 'Exportar para planilha (xlsx)'**
        opcao_xlsx = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".xlsx"))
        )   
        opcao_xlsx.click()
        register_log("info","Opção 'Exportar para planilha (xlsx)' clicada!")
```
5. **Aguarda a abertura e muda para nova aba de envio.**
```python
        # **Aguardar nova aba abrir**
        num_janelas_antes = len(navegador.window_handles)

        # Espera até que uma nova aba seja aberta (timeout de 10s)
        for _ in range(10):
            if len(navegador.window_handles) > num_janelas_antes:
                break
            time.sleep(1)  # Espera 1s antes de verificar novamente

        # **Mudar para a nova aba**
        janelas = navegador.window_handles
        navegador.switch_to.window(janelas[-1])  # Muda para a última aba (a que foi aberta)
        register_log("info", "Acessou a janela de envio no email")
```

6. **Preenche os campos do formulário de envio por e-mail.**
    - Chama a função que abre o formulário
    ```python
    try:
         navegador.execute_script("showEmailForm()") # Chama a função que abre o formulario para enfiar no email
    ```
    - Insere o endereço de email
    ```python
        # Espera até que o campo de Destinatario esteja visível e interativo
        Para_input = wait.until(
            EC.element_to_be_clickable((By.ID, "textPara"))
        )
        Para_input.send_keys("") # Digita Email
    ```
    - Coloca o Titulo do email
      ```python
        # Espera até que o campo de Assunto esteja visível e interativo
        Assunto_input = wait.until(
            EC.element_to_be_clickable((By.ID, "textAssunto"))
        )
        Assunto_input.clear()
        Assunto_input.send_keys(f"Estoque do dia {date.today()}") # Digita o assunto email  
        ```
7. **Envia o e-mail com a planilha anexada.**
```python
            navegador.execute_script("sendEmail()") # Chama a função para enviar o email
            register_log("info", "Enviou email")
```
8. **Fecha a aba de envio e retorna para a página principal.**
```python
            time.sleep(3)
            navegador.close()
            register_log("info", "Fechou Janela")
        except Exception as e:
            register_log("error",f"Erro capturado: {e}")
            
        navegador.switch_to.window(janelas[0]) # volta para a pagina q estava
```

### **Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `navegador` | `webdriver` | Instância do navegador Selenium. |

### **Retorno:**
- Nenhum. A função apenas executa a exportação e envio do arquivo.

### **Erros Tratados:**
- Caso ocorra um erro ao exportar a tabela, a exceção é propagada para ser tratada na `main()`.
```python
except Exception as e:
      raise ValueError(f"Erro ao tentar exportar a tabela: {e}") # Propaga o erro para o main()
```

---

## `Função: verifica_download()`

Verifica se o arquivo de estoque foi baixado com sucesso.

### **Fluxo da função:**
1. **Lista os arquivos no diretório de download.**
```python
  arquivos = os.listdir(diretorio)  # Lista todos os arquivos no diretório
```
2. **Verifica se o arquivo esperado está presente.**
```python
for arquivo in arquivos:
      if "arquivo.xlsx" in arquivo:  # Verifica se o nome contém a string desejada
          caminho_arquivo = os.path.join(diretorio, arquivo)
          register_log("info",f"Arquivo abaixado: {caminho_arquivo}")
          return True
```
3. **Aguarda até 10 segundos pelo download antes de gerar um erro.**
```python
for _ in range(10):
        arquivos = os.listdir(diretorio)  # Lista todos os arquivos no diretório
        for arquivo in arquivos:
            if "arquivo.xlsx" in arquivo:  # Verifica se o nome contém a string desejada
                caminho_arquivo = os.path.join(diretorio, arquivo)
                register_log("info",f"Arquivo abaixado: {caminho_arquivo}")
                return True
        time.sleep(1)  # Aguarda 1 segundo antes de tentar novamente
```


### **Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `diretorio` | `str` | Caminho do diretório onde o arquivo deve ser salvo. |

### **Retorno:**
- `True` se o arquivo foi localizado.
- Gera um erro se o arquivo não for encontrado.
```python
raise ValueError("Arquivo não localizado")
```

---

## `Função: sair_sankhya()`

Realiza o logout do sistema Sankhya, para não acumular licenças em uso.

### **Fluxo da função:**
1. **Define um tempo maximo para esperar o elemento**
```python
wait = WebDriverWait(navegador, 10)  # Tempo máximo de espera de 10 segundos
```

2. **Clica no ícone do usuário para abrir o menu.**
```python
  # Clicar no ícone do usuário
  icone_usuario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".icon-user-photo")))
  icone_usuario.click()

  time.sleep(1)  # Pequena pausa para o menu abrir
```

3. **Clica no botão "Sair" via JavaScript.**
```python
    #Clica no button sair pelo javascript
    navegador.execute_script("document.querySelector('body > div.gwt-PopupPanel.ContextMenuPopup > div > table > tbody > tr:nth-child(2) > td > div > table > tbody > tr:nth-child(16) > td').click()")  
```

4. **Registra no log que o logout foi realizado.**
```python
register_log("info","Deslogando")
```

### **Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `navegador` | `webdriver` | Instância do navegador Selenium. |

### **Retorno:**
- Nenhum. Apenas realiza o logout da plataforma.

### **Erros Tratados:**
- Caso ocorra um erro ao clicar no botão de logout, a exceção é propagada para a `main()`.
```python
except Exception as e:
        raise ValueError(f"Erro ao clicar no elemento: {e}") # Propaga o erro para o main()
```
---
## `Função: organiza_arquivo()`

Organiza e renomeia o arquivo de estoque baixado.

### **Fluxo da função:**
1. **Localiza o arquivo mais recente na pasta de relatórios.**
```python
  arquivos = glob.glob(os.path.join(diretorio, "*.xlsx"))  # Lista arquivos .xlsx

  arquivos.sort(key=os.path.getmtime, reverse=True)  # Ordena do mais recente para o mais antigo
  arquivo_mais_recente = arquivos[0]  # Pega o mais recente
```

2. **Cria uma pasta com a data e hora atuais.**
```python
  try:
      data_hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Formato: YYYY-MM-DD_HH-MM-SS

      pasta_data = os.path.join(os.getcwd(), diretorio+'\\'+data_hora_atual)
      os.makedirs(pasta_data, exist_ok=True) # Criar pasta se não existir
```
3. **Move e renomeia o arquivo de estoque.**
```python
      novo_nome = f"Estoque_{data_hora_atual}.xlsx"
      novo_caminho = os.path.join(pasta_data, novo_nome)

      os.rename(arquivo_mais_recente, novo_caminho)  # Renomeia o arquivo
```
4. **Registra no log que o arquivo foi renomeado.**
```python
     register_log("info",f"Arquivo renomeado para: {novo_nome}")
```

### **Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `diretorio` | `dir` | Local onde os arquivos xlsx ficaram salvos. |

### **Retorno:**
- Caminho do arquivo renomeado.

### **Erros Tratados:**
- Caso ocorra um erro ao clicar no botão de logout, a exceção é propagada para a `main()`.
```python
 except Exception as e:
        raise ValueError(f"Nenhum Arquivo renomeado") # Propaga o erro para o main()
```
---

## `Função: filtra_separa_estoque()`

Filtra os produtos de estoque por loja e cria arquivos separados para **Empresa1** e **Empresa2**.

### **Fluxo da função:**
1. **Abre o arquivo Excel.**
```python
# Abrir o arquivo Excel
planilha = pd.read_excel(arquivo, skiprows=2) #skiprows pula as 2 primeiras linhas
```
2. **Calcula a coluna "Estoque Total".**
```python
  # Criar a nova coluna "Estoque Total" somando as colunas "I" e "J"
  # Verifique os nomes reais das colunas no DataFrame
  planilha['Estoque Total'] = planilha['Estoque'] - planilha['RESERVADO']

  # Remover as colunas "I" e "J"
  planilha.drop(columns=['Estoque', 'RESERVADO'], inplace=True)
```
3. **Filtra os produtos para venda das lojas "L-VENDA" (Empresa1) e "B-VENDA" (Empresa2).**
```python
    # Filtra os produtos da Empresa1 pronto para a venda
    produtos_empresa1 = ["L-VENDA"] # Valor desejado
    coluna_to_filtro = planilha.columns.tolist().index('Local') #pegar a posição da coluna 'Local'
    estoque_empresa1 = planilha[planilha.iloc[:, coluna_to_filtro].isin(produtos_empresa1)]

    # Filtra os produtos da Empresa2 pronto para a venda
    produtos_empresa2 = ["B-VENDA"] # Valor desejado
    coluna_to_filtro = planilha.columns.tolist().index('Local') #pegar a posição da coluna 'Local'
    estoque_empresa2 = planilha[planilha.iloc[:, coluna_to_filtro].isin(produtos_empresa2)]
```
4. **Deixa apenas as coluna "REFERENCIA", "Estoque Total" e "Produto"**
```python
    # Manter apenas as colunas "REFERENCIA","Estoque Total" e "Produto"
    # primary key -> REFERENCIA
    # foreign key -> Produto
    colunas_para_manter = ["REFERENCIA", "Estoque Total","Produto"]
    planilha_final_empresa1 = estoque_empresa1[colunas_para_manter]
    planilha_final_empresa2 = estoque_empresa2[colunas_para_manter]
```
4. **Salva os arquivos separados para cada loja e registra um log para cada.**
```python
diretorio = os.path.dirname(arquivo) #Pega o diretorio base
    
    # Salva o resultado final Empresa1
    New_nome_Arquivo = 'Empresa1_'+os.path.basename(arquivo) # Nome do Arquivo o prefixo Empresa1_
    planilha_final_empresa1.to_excel(diretorio+'\\'+New_nome_Arquivo, index=False) # Cria Arquivo
    arquivos = ({"Empresa1":diretorio+'\\'+New_nome_Arquivo}) # Adicionar o diretorio do arquivo para o retorno
    register_log("info",f"Planilha Empresa1 final salva em: {diretorio}\{New_nome_Arquivo}")

    # Salva o resultado final Empresa2
    New_nome_Arquivo = 'Empresa2_'+os.path.basename(arquivo) # Nome do Arquivo o prefixo Empresa2_
    planilha_final_empresa2.to_excel(diretorio+'\\'+New_nome_Arquivo, index=False) # Cria Arquivo
    arquivos.update({"Empresa2":diretorio+'\\'+New_nome_Arquivo}) # Adicionar o diretorio do arquivo para o retorno  
    register_log("info",f"Planilha Empresa2 final salva em: {diretorio}\{New_nome_Arquivo}")
```
### **Retorno:**
- Dicionário com os caminhos dos arquivos filtrados para cada loja.
```python
 return arquivos # retornar os diretorios dos arquivos de cada empresa
 ```

---


# Função: update_estoque_Empresa2()

Realiza a atualização do estoque da loja da Empresa2 através do painel administrativo da Tray.

## Fluxo da função:

1. **Acessa a página de importação da Tray**:
    ```python
    # Abrir Tray
    navegador.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # impede que o navegador identifique o Bot
    navegador.get("https://www.loja2.com.br/admin/#/importapp/import/send/product/110068")
    navegador.fullscreen_window()
    time.sleep(5)
    ```

2. **Faz login, caso necessário**:
    ```python
    # verifica se a pagina abriu no form de login
    if navegador.current_url == "https://loja-s.tray.com.br/adm/login.php" or navegador.title == "Backoffice E-Commerce Suite":
    ```
  - Registra log e acessa o formulario
  ```python
        register_log("info","Login tray Empresa2")
        # Acessa o formulario
        Formulario = navegador.find_element(By.ID, "UsuarioLoginForm")
  ```
  - Insere o Usuario
  ```python
        # Inserção do Usuario
        user_input = Formulario.find_element(By.ID, "usuario") # pega o input para inserir usuario
        user_input.send_keys("") # insere usuario 
  ```
  - Insere a Senha
  ```python
        # Inserção do Senha
        senha_input = Formulario.find_element(By.ID, "senha") # pega o input para inserir a Senha
        senha_input.send_keys("") # insere Senha
  ```
  - Preciona o ENTER
    ```python
        senha_input.send_keys(Keys.RETURN) # preciona Enter
        time.sleep(5)  
    ```

3. **Verifica se abriu autenticação de dois fatores**
```python
    #verifica se tem segundo fator
    url_atual = urlparse(navegador.current_url)
    if url_atual.netloc + url_atual.path == "www.loja2.com.br/mvc/adm/users/twoFactorAuth/5/login":
```
  - captura mensagem de erro
  ```python
        #captura info para saber em qual email foi o codigo de segundo fator
        elemento = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "form .enter-the-code .ls-label-text.ls-no-bold:not(.rememberme)")
            )
        )
  ```
  - Cria erro e propaga para a main()`
  ```pyhton
        raise ValueError(f"código de segurança - {elemento.text}") # Propaga o erro para o main()
  ```
4. **Verifica senha expirada**:
```python
    #verifica se a senha expirou
    if navegador.current_url == "https://www.loja2.com.br/mvc/adm/login/password_expired":
```
  - captura mensagem de erro
  ```python
       #captura mensagem de senha expirada
        elemento = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ls-alert-danger")
            )
        )
  ```
  - Cria erro e propaga para a main()`
  ```pyhton
        raise ValueError(f"Senha Expirada - {elemento.text}") # Propaga o erro para o main()
  ```
5. **Acessa o aplicativo de importação de estoque**:
  - Verifica se já abriu no aplicativo e registra o log
    ```python
    if navegador.current_url != "https://www.loja2.com.br/admin/#/importapp/import/send/product/110068":
        register_log("info","Acessando aplicativo de importação")
    ```
  - Abre a loja de APPs e espera carregar todos os aplicativos
  ```python
        # abre a loja de aplicativos
        navegador.get("https://www.loja2.com.br/auth.php?new_apps_list=1")
        #WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
        # Aguarda até a lista de apps carregar
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "box-list-apps"))
        )
  ```
  - Procura o APP "Importação de dados via Excel" pelo nome
  ```python
  # Encontrar o aplicativo pelo nome
      title_apps = navegador.find_elements(By.CLASS_NAME, "appstore-title-app > a")
      for nome in title_apps:
          if "Importação de dados via Excel" in nome.text:
              register_log("info","Aplicativo encontrado!")
              nome.click()
              break
  ```
  - Abre o aplicativo
  ```python
        # abre o aplicativo de importação
        navegador.get("https://www.loja2.com.br/importapp/import/dashboard/?store=1330215&adm_user=tideorbronze&user_id=5&store_plan_id=2839&url=https://www.loja2.com.br")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
  ```
  - Acesssa o formulario com a opção "Atualiza estoque"
  ```python
        navegador.get("https://www.loja2.com.br/admin/#/importapp/import/send/product/110068")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
  ```

6. **Seleciona e envia o arquivo Excel com o estoque atualizado**:
  - Acessa o iframe e registra log
    ```python
    wait = WebDriverWait(navegador, 5)  # Tempo máximo de espera de 5 segundos
    try:
        iframe = wait.until(EC.presence_of_element_located((By.ID, "centro")))
        navegador.switch_to.frame(iframe)
        register_log("info","Mudou para o iframe!")
        time.sleep(2) # Faz funcionar
    ```
  - Seleciona input e sube arquivo excel
    ```python
        # **Seleciona input de arquivos**
        input_file = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        input_file.send_keys(dir_arquivos) #insere o arquivo excel       
        register_log("info","insere o Excel")
    ```

7. **Confirma a importação e aguarda a conclusão**:
  - Clica no Botão de "Iniciar Importação" e registra logo
    ```python 
        # ** Clicar na botão 'Iniciar Importação'**
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        register_log("info","'Iniciar Importação' clicada!")
    ```
  - Confirma a importação e registra log
  ```python
        # Esperar o modal abrir
        wait.until(EC.presence_of_element_located((By.ID, "modal-clean-stock-inactive-items")))

        # Clicar no botão "Importar excel, inativar e zerar o estoque de produtos ausentes"
        botao_importar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tray-tst='import.modal-clean-stock-inactive-items.continue']")))
        botao_importar.click()
        register_log("info","Importação iniciada!")
  ```
  - Aguarda importação terminar e redireciona
  ```python
      # Espera por 15 segundos para fazer o upload
        for _ in range(15):
            print(f"{_+1}s")
            time.sleep(1) 

        # Procura o botão de lista de produtos por 20s 
        botao_lista_produtos = WebDriverWait(navegador, 20).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.ls-btn-primary")
        ))
        botao_lista_produtos.click()
        register_log("info","Upload concluído! Redirecionando para a lista de produtos.")
        time.sleep(2) 
  ```

## Parâmetros:

| Parâmetro   | Tipo       | Descrição                                      |
|-------------|------------|------------------------------------------------|
| dir_arquivos | str        | Caminho do arquivo Excel a ser importado.     |
| navegador    | WebDriver  | Instância do Selenium WebDriver.              |

## Retorno:

A função não retorna valores, apenas executa o processo de atualização.

## Erros Tratados:

Caso ocorra erro no processo de importação, a exceção é propagada:
```python
except Exception as e:
        raise ValueError(f"Erro no Importação Empresa2: {e}") # Propaga o erro para o main()
```


# Função: update_estoque_Empresa1()

Realiza a atualização do estoque da loja da Empresa1 através do painel administrativo da Tray.

## Fluxo da função:

1. **Acessa a página de importação da Tray**:
    ```python
    #Abrir Tray
    #navegador.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # impede que o navegador identifique o Bot
    navegador.get("https://www.loja1.com.br/admin/#/importapp/import/send/product/110074")
    navegador.fullscreen_window()
    time.sleep(5)  
    ```

2. **Faz login, caso necessário**:
```python
    #verifica se a pagina abriu no form de login
    if navegador.current_url == "https://loja-s.tray.com.br/adm/login.php" or navegador.title == "Backoffice E-Commerce Suite":  
    ```
  - Registra log e acessa o formulario
  ```python
    register_log("info","Login tray Empresa1")
    # Acessa o formulario
    Formulario = navegador.find_element(By.ID, "UsuarioLoginForm")
  ```
  - Insere o Usuario
  ```python
    # Inserção do Usuario
    user_input = Formulario.find_element(By.ID, "usuario") # pega o input para inserir usuario
    user_input.send_keys("") # insere usuario 
  ```
  - Insere a Senha
  ```python
    # Inserção do Senha
    senha_input = Formulario.find_element(By.ID, "senha") # pega o input para inserir a Senha
    senha_input.send_keys("") # insere Senha
  ```
  - Preciona o ENTER
    ```python
    senha_input.send_keys(Keys.RETURN) # preciona Enter
    time.sleep(5)   
    ```

3. **Verifica se abriu autenticação de dois fatores**
```python
    #verifica se tem segundo fator
    url_atual = urlparse(navegador.current_url)
    if url_atual.netloc + url_atual.path == "www.loja1.com.br/mvc/adm/users/twoFactorAuth/5/login":
```
  - captura mensagem de erro
  ```python
    #captura info para saber em qual email foi o codigo de segundo fator
    elemento = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "form .enter-the-code .ls-label-text.ls-no-bold:not(.rememberme)")
        )
    )
  ```
  - Cria erro e propaga para a main()
  ```pyhton
      raise ValueError(f"código de segurança - {elemento.text}") # Propaga o erro para o main()
  ```
4. **Verifica senha expirada**:
```python
  #verifica se a senha expirou
  if navegador.current_url == "https://www.loja1.com.br/mvc/adm/login/password_expired":
```
  - captura mensagem de erro
  ```python
    #captura mensagem de senha expirada
    elemento = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".ls-alert-danger")
        )
    )
  ```
  - Cria erro e propaga para a main()`
  ```pyhton
        raise ValueError(f"Senha Expirada - {elemento.text}") # Propaga o erro para o main()
  ```

5. **Acessa o aplicativo de importação de estoque**:
  - Verifica se já abriu no aplicativo e registra o log
    ```python
    #verificar se abriu na pagina certa
    if navegador.current_url != "https://www.loja1.com.br/admin/#/importapp/import/send/product/110074":
        register_log("info","Acessando aplicativo de importação")
    ```
  - Abre a loja de APPs e espera carregar todos os aplicativos
  ```python
        # abre a loja de aplicativos
        navegador.get("https://www.loja1.com.br/auth.php?new_apps_list=1")
        #WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
        # Aguarda até a lista de apps carregar
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "box-list-apps"))
        )
  ```
  - Procura o APP "Importação de dados via Excel" pelo nome
  ```python
         # Encontrar o aplicativo pelo nome
        title_apps = navegador.find_elements(By.CLASS_NAME, "appstore-title-app > a")
        for nome in title_apps:
            if "Importação de dados via Excel" in nome.text:
                register_log("info","Aplicativo encontrado!")
                nome.click()
                break
  ```
  - Abre o aplicativo
  ```python
        # abre o aplicativo de importação  
        navegador.get("https://www.loja1.com.br/importapp/import/dashboard/?store=659928&adm_user=&user_id=19&store_plan_id=2799&url=https://www.loja1.com.br")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
  ```
  - Acesssa o formulario com a opção "Atualiza estoque"
  ```python
        # abre no formulario com a opção "Atualiza estoque" selecionada
        navegador.get("https://www.loja1.com.br/admin/#/importapp/import/send/product/110074")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
  ```

6. **Seleciona e envia o arquivo Excel com o estoque atualizado**:
  - Acessa o iframe e registra log
    ```python
    wait = WebDriverWait(navegador, 5)  # Tempo máximo de espera de 5 segundos
    try:
        iframe = wait.until(EC.presence_of_element_located((By.ID, "centro")))
        navegador.switch_to.frame(iframe)
        register_log("info","Mudou para o iframe!")
        time.sleep(2) # Faz funcionar
    ```
  - Seleciona input e sube arquivo excel
    ```python
        # **Seleciona input de arquivos**
        input_file = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        input_file.send_keys(dir_arquivos) #insere o arquivo excel       
        register_log("info","inseri o Excel")
    ```

7. **Confirma a importação e aguarda a conclusão**:
  - Clica no Botão de "Iniciar Importação" e registra logo
    ```python  
        # ** Clicar na botão 'Iniciar Importação'**
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        register_log("info","'Iniciar Importação' clicada!")
    ```
  - Confirma a importação e registra log
  ```python
        # Esperar o modal abrir
        wait.until(EC.presence_of_element_located((By.ID, "modal-clean-stock-inactive-items")))

        # Clicar no botão "Importar excel, inativar e zerar o estoque de produtos ausentes"
        botao_importar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tray-tst='import.modal-clean-stock-inactive-items.continue']")))
        botao_importar.click()
        register_log("info","Importação iniciada!")
  ```
  - Aguarda importação terminar e redireciona
  ```python
        # Espera por 20 segundos para fazer o upload
        for _ in range(20):
            print(f"{_+1}s")
            time.sleep(1) 
        print("espera +20s")
        # Procura o botão de lista de produtos por 20s 
        botao_lista_produtos = WebDriverWait(navegador, 25).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.ls-btn-primary")
        ))
        botao_lista_produtos.click()
        register_log("info","Upload concluído! Redirecionando para a lista de produtos.")
        time.sleep(2) 
  ```

## Parâmetros:

| Parâmetro   | Tipo       | Descrição                                      |
|-------------|------------|------------------------------------------------|
| dir_arquivos | str        | Caminho do arquivo Excel a ser importado.     |
| navegador    | WebDriver  | Instância do Selenium WebDriver.              |

## Retorno:

A função não retorna valores, apenas executa o processo de atualização.

## Erros Tratados:

Caso ocorra erro no processo de importação, a exceção é propagada:
```python
except Exception as e:
        raise ValueError(f"Erro no Importação Empresa1: {e}") # Propaga o erro para o main()
```

# Função: main()

Executa o processo automatizado de atualização do estoque, incluindo login no Sankhya, exportação de dados, processamento e upload para as lojas da Empresa1 e Empresa2.

## Fluxo da função:

1. **Registra o início da atualização**:
    ```python
    register_log("info","Atualização Iniciada.")
    ```

2. **Define diretório e configura navegador**:
    ```python
    Diretorio = r"\relatório"
    view_navigator = False  # Habilita ou desabilita a visualização do navegador
    driver = config_browser(Diretorio, view_navigator, True)  # Configura o navegador Edge
    ```

3. **Executa as etapas para buscar dados no SANKHYA**:
    ```python
    try:
        login_sankhya(driver)  # Faz login no Sankhya
        pesquisar_estoque(driver)  # Acessa o painel "Estoque Reservado"
        exportar_tabela(driver)  # Faz download e envia os dados por e-mail
        verifica_download(Diretorio)  # Verifica se o download foi concluído
        sair_sankhya(driver)  # Realiza logoff do Sankhya para evitar bloqueios de licença
    ```

4. **Organiza e filtra os arquivos baixados**:
    ```python
        Arquivo_estoque = organiza_arquivo(Diretorio)  # Renomeia e move o arquivo baixado
        Arquivos_filtrados = filtra_separa_estoque(Arquivo_estoque)  # Separa os dados entre Empresa1 e Empresa2
    ```

5. **Realiza o upload dos estoques para as lojas**:
    ```python
        update_estoque_Empresa2(Arquivos_filtrados["Empresa2"], driver)  # Atualiza estoque da Empresa2
        update_estoque_Empresa1(Arquivos_filtrados["Empresa1"], driver)  # Atualiza estoque da Empresa1
        time.sleep(5)
    ```

6. **Registra sucesso ao final do processo**:
    ```python
        register_log("sucesso", "Atualização feita com sucesso")
    ```

7. **Captura erro caso ocorra falha no processo**:
    ```python
    except Exception as e:
        if driver:
            captura_screenshot(driver, "warning", f"Erro capturado: {e}")
        else:
            register_log("warning", f"Erro capturado: {e}")
    ```

8. **Finaliza o processo e fecha o navegador**:
    ```python
    finally:
        if driver:
            driver.quit()
            register_log("info","Atualização finalizada.")
    ```

## Parâmetros:

A função `main()` não recebe parâmetros.

## Retorno:

A função não retorna valores, apenas executa o processo de atualização.

## Erros Tratados:

- Se ocorrer um erro durante a execução, um screenshot será capturado (se o navegador estiver aberto) ou o erro será registrado no log.
```python
except Exception as e:
    if driver:
        captura_screenshot(driver, "warning", f"Erro capturado: {e}")
    else:
        register_log("warning", f"Erro capturado: {e}")

