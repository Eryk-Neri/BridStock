from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from datetime import date
from datetime import datetime
from log import *
import glob
import time
import pandas as pd
import os

def config_browser(diretorio=r"\relatório", headless=False, debug=False):
    pasta_download = os.path.join(os.getcwd(), diretorio)
    os.makedirs(pasta_download, exist_ok=True) # Criar pasta se não existir

    edge_options = webdriver.EdgeOptions()

    if debug:
        #Se quiser manter o navegador aberto mesmo após o script terminar
        edge_options.add_experimental_option("detach", True)
    
    if not headless:
        edge_options.add_argument("--headless")  # Rodar sem interface gráfica (remova se quiser ver a UI)
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

    return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=edge_options)

def login_sankhya(navegador):
    #Abrir Sankhya
    navegador.get("")
    navegador.fullscreen_window()
    time.sleep(5)

    # Acessar o Shadow DOM dentro do Web Component <sankhya-login>
    shadow_root = navegador.execute_script("return arguments[0].shadowRoot", navegador.find_element(By.TAG_NAME, "sankhya-login"))
    
    #inserção do Usuario
    user_input = shadow_root.find_element(By.ID, "user")  #pega o input para inserir usuario
    user_input.send_keys("") #Insere usuario sup
    user_input.send_keys(Keys.RETURN) #preciona Enter

    #inserção do Senha
    user_input = shadow_root.find_element(By.ID, "password")  #pega o input para inserir a Senha
    user_input.send_keys("") #Insere Senha
    user_input.send_keys(Keys.RETURN) #preciona Enter

    time.sleep(20)

def pesquisar_estoque(navegador):
    try:
        # Espera até que o campo de pesquisa esteja visível e interativo
        search_input = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.ID, "search-input-element"))
        )
        search_input.send_keys("ESTOQUE RESERVADO") # Digita "ESTOQUE RESERVADO" 
        time.sleep(2)     
        search_input.send_keys(Keys.RETURN) # Pressiona ENTER para pesquisar
        register_log("info","Pesquisa realizada com sucesso!")
    
    except Exception as e:
        raise ValueError(f"Erro ao pesquisar: {e}") # Propaga o erro para o main()

def exportar_tabela(navegador):
    wait = WebDriverWait(navegador, 20)  # Tempo máximo de espera de 20 segundos
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "gwt-Frame")))
        register_log("info","Mudou para o iframe!")

        # ** Clicar no botão de exportação principal**
        botao_exportar = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "sk-grid-printer button.btn-default.dropdown-toggle"))
        )
        botao_exportar.click()
        register_log("info","Botão de exportação clicado!")

        # ** Aguardar a popover aparecer**
        wait.until(EC.visibility_of_element_located((By.ID, "sk-popover-002")))
        time.sleep(1)  # Pequena pausa para garantir a renderização

        # ** Clicar na opção 'Exportar para planilha (xlsx)'**
        opcao_xlsx = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".xlsx"))
        )
        opcao_xlsx.click()
        register_log("info","Opção 'Exportar para planilha (xlsx)' clicada!")
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

        try:
            navegador.execute_script("showEmailForm()") # Chama a função que abre o formulario para enfiar no email
            # Espera até que o campo de Destinatario esteja visível e interativo
            Para_input = wait.until(
                EC.element_to_be_clickable((By.ID, "textPara"))
            )
            Para_input.send_keys("") # Digita Email

            # Espera até que o campo de Assunto esteja visível e interativo
            Assunto_input = wait.until(
                EC.element_to_be_clickable((By.ID, "textAssunto"))
            )
            Assunto_input.clear()
            Assunto_input.send_keys(f"Estoque do dia {date.today()}") # Digita o assunto email  
            navegador.execute_script("sendEmail()") # Chama a função para enviar o email
            register_log("info", "Enviou email")

            time.sleep(3)
            navegador.close() 
            register_log("info", "Fechou Janela")
        except Exception as e:
            register_log("error",f"Erro capturado: {e}")
            
        navegador.switch_to.window(janelas[0]) # volta para a pagina q estava 

    except Exception as e:
        raise ValueError(f"Erro ao tentar exportar a tabela: {e}") # Propaga o erro para o main()

def verifica_download(diretorio=r"\relatório"):
    for _ in range(10):
        arquivos = os.listdir(diretorio)  # Lista todos os arquivos no diretório
        for arquivo in arquivos:
            if "arquivo.xlsx" in arquivo:  # Verifica se o nome contém a string desejada
                caminho_arquivo = os.path.join(diretorio, arquivo)
                register_log("info",f"Arquivo abaixado: {caminho_arquivo}")
                return True
        time.sleep(1)  # Aguarda 1 segundo antes de tentar novamente
    raise ValueError("Arquivo não localizado")

def sair_sankhya(navegador):
    try:
        wait = WebDriverWait(navegador, 10)

        # Clicar no ícone do usuário
        icone_usuario = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".icon-user-photo")))
        icone_usuario.click()
        
        time.sleep(1)  # Pequena pausa para o menu abrir

        #Clica no button sair pelo javascript
        navegador.execute_script("document.querySelector('body > div.gwt-PopupPanel.ContextMenuPopup > div > table > tbody > tr:nth-child(2) > td > div > table > tbody > tr:nth-child(16) > td').click()")
        register_log("info","Deslogando")
        #navegador.quit()
    
    except Exception as e:
        raise ValueError(f"Erro ao clicar no elemento: {e}") # Propaga o erro para o main()

def organiza_arquivo(diretorio=r"\relatório"):
    arquivos = glob.glob(os.path.join(diretorio, "*.xlsx"))  # Lista arquivos .xlsx

    arquivos.sort(key=os.path.getmtime, reverse=True)  # Ordena do mais recente para o mais antigo
    arquivo_mais_recente = arquivos[0]  # Pega o mais recente

    try:
        data_hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Formato: YYYY-MM-DD_HH-MM-SS

        pasta_data = os.path.join(os.getcwd(), diretorio+'\\'+data_hora_atual)
        os.makedirs(pasta_data, exist_ok=True) # Criar pasta se não existir

        novo_nome = f"Estoque_{data_hora_atual}.xlsx"
        novo_caminho = os.path.join(pasta_data, novo_nome)

        os.rename(arquivo_mais_recente, novo_caminho)  # Renomeia o arquivo

        register_log("info",f"Arquivo renomeado para: {novo_nome}")
        return novo_caminho
    except Exception as e:
        raise ValueError(f"Nenhum Arquivo renomeado") # Propaga o erro para o main()

def filtra_separa_estoque(arquivo):
    # Abrir o arquivo Excel
    planilha = pd.read_excel(arquivo, skiprows=2) #skiprows pula as 2 primeiras linhas
    
    # Criar a nova coluna "Estoque Total" somando as colunas "I" e "J"
    # Verifique os nomes reais das colunas no DataFrame
    planilha['Estoque Total'] = planilha['Estoque'] - planilha['RESERVADO']

    # Remover as colunas "I" e "J"
    planilha.drop(columns=['Estoque', 'RESERVADO'], inplace=True)

    # Filtra os produtos da Empresa1 pronto para a venda
    produtos_empresa1 = ["L-VENDA"] # Valor desejado
    coluna_to_filtro = planilha.columns.tolist().index('Local') #pegar a posição da coluna 'Local'
    estoque_empresa1 = planilha[planilha.iloc[:, coluna_to_filtro].isin(produtos_empresa1)]

    # Filtra os produtos da Empresa2 pronto para a venda
    produtos_empresa2 = ["B-VENDA"] # Valor desejado
    coluna_to_filtro = planilha.columns.tolist().index('Local') #pegar a posição da coluna 'Local'
    estoque_empresa2 = planilha[planilha.iloc[:, coluna_to_filtro].isin(produtos_empresa2)]

    # Manter apenas as colunas "REFERENCIA","Estoque Total" e "Produto"
    # primary key -> REFERENCIA
    # foreign key -> Produto
    colunas_para_manter = ["REFERENCIA", "Estoque Total","Produto"]
    planilha_final_empresa1 = estoque_empresa1[colunas_para_manter]
    planilha_final_empresa2 = estoque_empresa2[colunas_para_manter]

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

    return arquivos # retornar os diretorios dos arquivos de cada empresa 

def update_estoque_Empresa2(dir_arquivos,navegador):

    # Abrir Tray
    navegador.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # impede que o navegador identifique o Bot
    navegador.get("https://www.loja2.com.br/admin") #Loja Tray da Empresa2
    navegador.fullscreen_window()
    time.sleep(5)

    # verifica se a pagina abriu no form de login
    if navegador.current_url == "https://loja-s.tray.com.br/adm/login.php" or navegador.title == "Backoffice E-Commerce Suite": 
        register_log("info","Login tray Empresa2")
        # Acessa o formulario
        Formulario = navegador.find_element(By.ID, "UsuarioLoginForm")
        
        # Inserção do Usuario
        user_input = Formulario.find_element(By.ID, "usuario") # pega o input para inserir usuario
        user_input.send_keys("") # insere usuario 

        # Inserção do Senha
        senha_input = Formulario.find_element(By.ID, "senha") # pega o input para inserir a Senha
        senha_input.send_keys("") # insere Senha
        
        senha_input.send_keys(Keys.RETURN) # preciona Enter
        time.sleep(5)  
    
    #verifica se tem segundo fator
    url_atual = urlparse(navegador.current_url)
    if url_atual.path.startswith('/mvc/adm/users/twoFactorAuth/'):
        #captura info para saber em qual email foi o codigo de segundo fator
        elemento = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "form .enter-the-code .ls-label-text.ls-no-bold:not(.rememberme)")
            )
        )
    
        raise ValueError(f"código de segurança - {elemento.text}") # Propaga o erro para o main()
    
    #verifica se a senha expirou
    if navegador.current_url == "https://www.loja2.com.br/mvc/adm/login/password_expired": 
        #captura mensagem de senha expirada
        elemento = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ls-alert-danger")
            )
        )
        raise ValueError(f"Senha Expirada - {elemento.text}") # Propaga o erro para o main()

    # verificar se abriu na pagina certa
    if navegador.current_url != "https://www.loja2.com.br/admin/#/importapp/import/send/product/110068":
        register_log("info","Acessando aplicativo de importação")
        # caso não abra
        # abre a loja de aplicativos
        navegador.get("https://www.loja2.com.br/auth.php?new_apps_list=1") 
        #WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
        # Aguarda até a lista de apps carregar
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "box-list-apps"))
        )

        # Encontrar o aplicativo pelo nome
        title_apps = navegador.find_elements(By.CLASS_NAME, "appstore-title-app > a")
        for nome in title_apps:
            if "Importação de dados via Excel" in nome.text:
                register_log("info","Aplicativo encontrado!")
                nome.click()
                break
        
        # abre o aplicativo de importação
        navegador.get("https://www.loja2.com.br/importapp/import/dashboard/?store=1330215&adm_user=&user_id=5&store_plan_id=2839&url=https://www.loja2.com.br")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s

        # abre no formulario com a opção "Atualiza estoque" selecionada
        navegador.get("https://www.loja2.com.br/admin/#/importapp/import/send/product/110068")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
    
    wait = WebDriverWait(navegador, 5)  # Tempo máximo de espera de 5 segundos
    try:
        iframe = wait.until(EC.presence_of_element_located((By.ID, "centro")))
        navegador.switch_to.frame(iframe)
        register_log("info","Mudou para o iframe!")
        time.sleep(2) # Faz funcionar

        # **Seleciona input de arquivos**
        input_file = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        input_file.send_keys(dir_arquivos) #insere o arquivo excel       
        register_log("info","insere o Excel")

        # ** Clicar na botão 'Iniciar Importação'**
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        register_log("info","'Iniciar Importação' clicada!")

        # Esperar o modal abrir
        wait.until(EC.presence_of_element_located((By.ID, "modal-clean-stock-inactive-items")))

        # Clicar no botão "Importar excel, inativar e zerar o estoque de produtos ausentes"
        botao_importar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tray-tst='import.modal-clean-stock-inactive-items.continue']")))
        botao_importar.click()
        register_log("info","Importação iniciada!")

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
    except Exception as e:
        raise ValueError(f"Erro no Importação Empresa2: {e}") # Propaga o erro para o main()

    #navegador.quit()

def update_estoque_Empresa1(dir_arquivos,navegador):
    
    #Abrir Tray
    #navegador.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # impede que o navegador identifique o Bot
    navegador.get("https://www.loja1.com.br/admin/")
    navegador.fullscreen_window()
    time.sleep(5)  

    #verifica se a pagina abriu no form de login
    if navegador.current_url == "https://loja-s.tray.com.br/adm/login.php" or navegador.title == "Backoffice E-Commerce Suite": 
        register_log("info","Login tray Empresa1")
        # Acessa o formulario
        Formulario = navegador.find_element(By.ID, "UsuarioLoginForm")
        
        # Inserção do Usuario
        user_input = Formulario.find_element(By.ID, "usuario") # pega o input para inserir usuario
        user_input.send_keys("") # insere usuario 

        # Inserção do Senha
        senha_input = Formulario.find_element(By.ID, "senha") # pega o input para inserir a Senha
        senha_input.send_keys("") # insere Senha

        senha_input.send_keys(Keys.RETURN) # preciona Enter
        time.sleep(5)  

    #verifica se tem segundo fator
    url_atual = urlparse(navegador.current_url)
    if url_atual.path.startswith('/mvc/adm/users/twoFactorAuth/'):
        #captura info para saber em qual email foi o codigo de segundo fator
        elemento = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "form .enter-the-code .ls-label-text.ls-no-bold:not(.rememberme)")
            )
        )

        raise ValueError(f"código de segurança - {elemento.text}") # Propaga o erro para o main()
    
    #verifica se a senha expirou
    if navegador.current_url == "https://www.loja2.com.br/mvc/adm/login/password_expired": 
        #captura mensagem de senha expirada
        elemento = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ls-alert-danger")
            )
        )
        raise ValueError(f"Senha Expirada - {elemento.text}") # Propaga o erro para o main()

    #verificar se abriu na pagina certa
    if navegador.current_url != "https://www.loja2.com.br/admin/#/importapp/import/send/product/110074":
        register_log("info","Acessando aplicativo de importação")
        # caso não abra
        # abre a loja de aplicativos
        navegador.get("https://www.loja2.com.br/auth.php?new_apps_list=1")
        #WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
        # Aguarda até a lista de apps carregar
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "box-list-apps"))
        )

        # Encontrar o aplicativo pelo nome
        title_apps = navegador.find_elements(By.CLASS_NAME, "appstore-title-app > a")
        for nome in title_apps:
            if "Importação de dados via Excel" in nome.text:
                register_log("info","Aplicativo encontrado!")
                nome.click()
                break
        
        # abre o aplicativo de importação  
        navegador.get("https://www.loja2.com.br/importapp/import/dashboard/?store=659928&adm_user=&user_id=19&store_plan_id=2799&url=https://www.loja2.com.br")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
 
        # abre no formulario com a opção "Atualiza estoque" selecionada
        navegador.get("https://www.loja2.com.br/admin/#/importapp/import/send/product/110074")
        WebDriverWait(navegador, 20).until(lambda d: d.execute_script("return document.readyState") == "complete") # espera carregar completamente por 20s
     
    wait = WebDriverWait(navegador, 5)  # Tempo máximo de espera de 5 segundos
    try:
        iframe = wait.until(EC.presence_of_element_located((By.ID, "centro")))
        navegador.switch_to.frame(iframe)
        register_log("info","Mudou para o iframe!")
        time.sleep(2) # Faz funcionar

        # **Seleciona input de arquivos**
        input_file = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        input_file.send_keys(dir_arquivos) #insere o arquivo excel       
        register_log("info","inseri o Excel")
        
        # ** Clicar na botão 'Iniciar Importação'**
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        register_log("info","'Iniciar Importação' clicada!")
        
        # Esperar o modal abrir
        wait.until(EC.presence_of_element_located((By.ID, "modal-clean-stock-inactive-items")))

        # Clicar no botão "Importar excel, inativar e zerar o estoque de produtos ausentes"
        botao_importar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-tray-tst='import.modal-clean-stock-inactive-items.continue']")))
        botao_importar.click()
        register_log("info","Importação iniciada!")
        
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
    except Exception as e:
        raise ValueError(f"Erro no Importação da Empresa1: {e}") # Propaga o erro para o main()

def main():
    register_log("info","Atualização Iniciada.")
    Diretorio = r"\relatório"
    view_navigator = True # Abilita ou desabilita a apção de ver o navegador rodando o robo
    driver = config_browser(Diretorio,view_navigator,True) # Faz toda a configuração e preferiencia do navegador Edge
    try:
        login_sankhya(driver) # Faz login no sankhya
        pesquisar_estoque(driver) # Acessa o painel "Estoque Reservado"
        exportar_tabela(driver) # Faz download e envia os dados por e-mail
        verifica_download(Diretorio) # Verifica se o download foi concluído
        sair_sankhya(driver) # Faz o logoff do sankhya para evitar o limite da lincenças
        Arquivo_estoque = organiza_arquivo(Diretorio) # renomear o "arquivo.xlsx" para "Estoque_{data e hora}" e colocar no diretorio
        Arquivos_filtrados = filtra_separa_estoque(Arquivo_estoque) # separa os dados do arquivo entre Empresa1 e Empresa2
        update_estoque_Empresa2(Arquivos_filtrados["Empresa2"],driver) # faz o Upload dos dados no loja(tray) da Empresa2
        update_estoque_Empresa1(Arquivos_filtrados["Empresa1"],driver) # faz o Upload dos dados no loja(tray) da Empresa1
        time.sleep(5)
        register_log("sucesso",f"Atualização feita com sucesso")
    except Exception as e:
        if driver:
            captura_screenshot(driver,"warning",f"Erro capturado: {e}")
        else:
            register_log("warning",f"Erro capturado: {e}")
    finally:
        if driver:
            driver.quit()
            register_log("info","Atualização finalizada.")
    

main()
