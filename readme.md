# Documentação - Controle de Estoque

## Projeto GitHub
Projeto Controle de Estoque;

## Visão Geral

Este projeto foi desenvolvido para automatizar a atualização de estoque entre o ERP Sankhya e a plataforma Tray, garantindo que os estoques estejam sempre sincronizados. Como o Tray não possui suporte nativo para integração com o Sankhya, um bot foi implementado utilizando **Python**, **Selenium** e **Pandas** para automatizar esse processo.

## Estrutura do Projeto

```
/BridStock
│── /logs                        # Arquivos de logs gerados pelo sistema  
│   ├── 2025-02-05_15-30-00/     # Diretório de logs único para cada execução
│   │   ├── log.json             # JSON contendo os registros detalhados
│   │   ├── log.log              # Arquivo de log convencional (INFO, ERROR, etc.)
│   │   ├── 15-31-22.png         # Screenshot do navegador (se houver)
│── /relatório  
│   ├── 2025-02-05_15-30-00/     # Diretório de relatório único para cada execução
│   │   ├── Empresa2_Estoque_2025-02-05_15-30-00.xlsx      # Planilha só com os produtos da Empresa2
│   │   ├── Empresa1_Estoque_2025-02-05_15-30-00.xlsx      # Planilha só com os produtos da Empresa1
│   │   ├── Estoque_2025-02-05_15-30-00.xlsx               # Planilha com todos os produtos extraido do sankhya
│── relatorio_estoque.py         # Script principal de automação
│── log.py                       # Módulo de gerenciamento de logs
│── docs/                        # Diretório de documentação
│   │── relatorio_estoque.md     # Documentação do script principal
│   │── log.md                   # Documentação do módulo de logs
│── readme.md                    # Documentação geral do projeto
```
## Requisitos do Projeto
- **Navegador Edge**
- **[Python 3.11](https://apps.microsoft.com/detail/9nrwmjp3717k?hl=neutral&gl=BR&ocid=pdpshare)**
    - `Selenium`
    - `Pandas`
    - `WebDriver Manager`
    - `openpyxl`
    - `logging`


## Fluxo da Automação
1. O bot faz login no **Sankhya**, acessa o painel **ESTOQUE RESERVADO** e exporta os dados em um arquivo Excel.
2. Os dados são processados para remover colunas desnecessárias e calcular o **Estoque total** (`Estoque - Reservado`).
3. O bot separa os produtos entre **Empresa1** e **Empresa2** com base na coluna Local (`L-VENDA` para Empresa1, `B-VENDA` para Empresa2).
4. Dois arquivos Excel são gerados: `Empresa1_Estoque_.xlsx` e `Empresa2_Estoque_.xlsx`.
5. O bot acessa o Tray e faz o upload dos arquivos para atualizar o estoque.

## Instalação e Configuração

1. **Clone o repositório**
   ```sh
   git clone https://github.com/Eryk-Neri/BridStock.git
   ```
2. **Instale as dependências**
   ```sh
   pip install selenium pandas webdriver-manager logging openpyxl
   ```
3. **Configuração**
   - Verifique o diretório `relatório` para garantir que os relatórios sejam armazenados corretamente.
   - Ajuste as credenciais de acesso no `relatorio_estoque.py`, se necessário.

## Como Executar

Execute o script principal:
```sh
python relatorio_estoque.py
```

Isso iniciará o processo de login no Sankhya, extração de dados, tratamento das informações e atualização do estoque nas lojas da Empresa1 e Empresa2.

## Documentação Específica

- Documentação do `relatorio_estoque.py` no arquivo relatorio_estoque.md
- Documentação do `log.py` no arquivo log.md