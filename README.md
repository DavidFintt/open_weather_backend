# OpenWeather Backend

API REST construida com FastAPI que consome o [OpenWeather SDK](https://github.com/DavidFintt/SDKOpenWeather) para consultar dados meteorologicos e publicar os resultados em um GitHub Gist.

## Funcionalidades

- Consulta de clima atual e previsao de 5 dias por cidade ou coordenadas
- Publicacao automatica dos resultados em um GitHub Gist
- Documentacao interativa via Swagger UI e ReDoc
- Validacao de parametros com mapeamento de erros HTTP
- Middleware de verificacao de variaveis de ambiente
- Testes automatizados executados durante o build Docker

## Endpoints

### GET /health

Retorna o status da aplicacao.

```json
{"status": "ok"}
```

### GET /weather

Consulta clima atual e previsao de 5 dias.

**Parametros (query string):**

| Parametro | Tipo  | Obrigatorio | Descricao              |
|-----------|-------|-------------|------------------------|
| `city`    | str   | Nao         | Nome da cidade         |
| `lat`     | float | Nao         | Latitude (-90 a 90)   |
| `lon`     | float | Nao         | Longitude (-180 a 180) |

Informe `city` ou `lat`/`lon`. Quando ambos sao enviados, coordenadas tem prioridade.

**Exemplo de requisicao:**

```
GET /weather?city=London
GET /weather?lat=-23.55&lon=-46.63
```

**Exemplo de resposta (200):**

```json
{
  "current": {
    "temp": 22,
    "description": "ceu limpo",
    "city": "Londres",
    "date": "14/03"
  },
  "forecast": [
    {"date": "15/03", "temp": 20},
    {"date": "16/03", "temp": 18}
  ],
  "gist_status": "Gist atualizado com sucesso"
}
```

**Codigos de erro:**

| Status | Causa                                     |
|--------|-------------------------------------------|
| 404    | Cidade nao encontrada / sem dados         |
| 422    | Parametros invalidos ou coordenadas fora do range |
| 429    | Limite de requisicoes da API excedido     |
| 500    | Chave de API invalida ou configuracao ausente |
| 502    | Erro na API do OpenWeather ou ao publicar gist |
| 503    | Servico temporariamente indisponivel      |
| 504    | Timeout na requisicao a API               |

## Documentacao Interativa

Com o servidor rodando, acesse:

- **Swagger UI:** http://localhost:8500/docs
- **ReDoc:** http://localhost:8500/redoc

## Configuracao

Crie um arquivo `.env` na raiz do projeto a partir do template:

```bash
cp .env.example .env
```

Preencha as variaveis:

| Variavel              | Descricao                          |
|-----------------------|------------------------------------|
| `OPENWEATHER_API_KEY` | Chave da API OpenWeatherMap        |
| `GITHUB_TOKEN`        | Token de acesso pessoal do GitHub  |
| `GIST_ID`             | ID do Gist a ser atualizado        |

O middleware bloqueia todas as requisicoes (exceto `/health`) caso alguma variavel esteja ausente.

## Execucao com Docker

```bash
# Build (executa os testes automaticamente)
docker build -t openweather-backend .

# Subir o container com um volume para o diretorio logs
docker run -d --network host --env-file .env -v $(pwd)/logs:/app/logs --name openweather-backend openweather-backend

# Execução de testes via docker
docker exec openweather-backend python -m pytest
```

```bash
# Build (executa os testes automaticamente)
docker build -t openweather-backend .

```

A API estara disponivel em `http://localhost:8500`.

## Execucao local (sem Docker)

```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Subir o servidor
uvicorn app.main:app --host 0.0.0.0 --port 8500
```

## Testes

Os testes usam `pytest` e nao fazem chamadas reais a APIs externas (todas as requisicoes sao mockadas).

```bash
python -m pytest tests/ -v
```

## Arquitetura

```
app/
    main.py              # Criacao do app, middleware e router
    config.py            # Carregamento de variaveis de ambiente
    middleware.py         # Verificacao de configuracao obrigatoria
    api/
        routes.py        # Endpoints HTTP
        mappings.py      # Mapeamento de excecoes para status HTTP
    core/
        service.py       # Logica de negocio e orquestracao
        exceptions.py    # Excecoes do backend
    adapters/
        weather_client.py  # Adapter para o OpenWeather SDK
        gist_client.py     # Adapter para o GitHub Gist
tests/
    conftest.py          # Fixtures compartilhadas
    test_config.py       # Testes de middleware e configuracao
    test_infrastructure.py # Health check
    test_weather.py      # Testes de consulta de clima
    test_sdk_errors.py   # Mapeamento de excecoes do SDK
    test_gist.py         # Publicacao no Gist
```

## Tecnologias

- Python 3.11
- FastAPI
- Uvicorn
- OpenWeather SDK
- PyGithub
- pytest / httpx (testes)
