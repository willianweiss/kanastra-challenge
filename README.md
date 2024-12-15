# Kanastra Challenge

## Requisitos
- Docker
- Docker Compose

## Como Rodar
1. Clone o repositório.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Inicie o ambiente com `docker-compose up`.
4. Acesse o endpoint em `http://localhost:8000/api/upload`.
5. Faça o upload do arquivo CSV.

## Testes
Rode os testes com:
```bash
pytest app/tests/
````

```
kanastra-challenge/
├── app/
│   ├── __init__.py
│   ├── main.py                   # Arquivo principal
│   ├── routers/
│   │   ├── __init__.py
│   │   └── upload.py             # Rotas de upload
│   ├── models/
│   │   ├── __init__.py
│   │   └── debt.py               # Modelo Debt
│   ├── services/
│   │   ├── __init__.py
│   │   ├── boleto_service.py     # Geração de boletos
│   │   ├── csv_processor.py      # Processamento do CSV
│   │   └── email_service.py      # Envio de e-mails
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── debt_processor.py     # Loop para processar dívidas pendentes
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py           # Configuração do banco de dados
│   └── utils/
│       ├── __init__.py
│       ├── config.py             # Configurações do projeto
│       └── logging.py            # Configuração de logs
├── .env                          # Variáveis de ambiente
├── requirements.txt              # Dependências do projeto
├── docker-compose.yml            # Orquestração com Docker
├── Dockerfile                    # Configuração do contêiner
```