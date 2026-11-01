# API de Tarefas (Flask + SQLite) no Azure

API REST básica em Python/Flask com banco SQLite, hospedada no Azure App Service (Linux, Python 3.12).

**URL da API:** https://api-sqlite-diogo.azurewebsites.net

## Endpoints

| Método | Endpoint | Função |
|--------|----------|--------|
| GET | `/` | Status da API |
| GET | `/tarefas` | Lista as tarefas |
| GET | `/tarefas/<id>` | Busca uma tarefa |
| POST | `/tarefas` | Cria uma tarefa (campo `titulo` obrigatório) |
| PUT | `/tarefas/<id>` | Atualiza uma tarefa |
| DELETE | `/tarefas/<id>` | Remove uma tarefa |

## Como rodar localmente

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
```

A API sobe em `http://localhost:5000`. O banco `app.db` é criado automaticamente.

## Exemplo de uso (PowerShell)

```powershell
Invoke-RestMethod -Method Post -Uri https://api-sqlite-diogo.azurewebsites.net/tarefas -ContentType "application/json" -Body '{"titulo":"Estudar Azure"}'
```

## Nuvem

- Azure App Service (plano B1, Linux), região East US 2
- Banco SQLite em `/home/data/app.db` (armazenamento persistente do App Service)
- Deploy a partir deste repositório (branch `main`)

## Autor

Diogo Henrique Assis Lozano - (RM568027) 
