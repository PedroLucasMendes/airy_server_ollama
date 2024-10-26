from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import logging
import json  # Importa o módulo JSON para análise

# Configurações de log para depuração
logging.basicConfig(level=logging.INFO)  # Configura o nível de log para INFO
logger = logging.getLogger(__name__)

# Inicializa a aplicação FastAPI
app = FastAPI()

# Configura o middleware de CORS (permite que outras origens acessem a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (use com cuidado em produção)
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Define o modelo para a entrada do usuário
class MessageRequest(BaseModel):
    message: str

# URL do Ollama API
OLLAMA_URL = "http://localhost:11434/api/generate"

# Endpoint principal para receber e responder mensagens
@app.post("/chat/")
async def chat(request: MessageRequest):
    logger.info(f"Recebido mensagem: {request.message}")

    try:
        # Envia a solicitação para o modelo local no Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": "llama3.2:1b",  # Modelo a ser utilizado
                    "prompt": request.message,
                },
                timeout=30.0  # Aumenta o tempo limite para 30 segundos
            )

        # Log da resposta bruta
        logger.info(f"Resposta bruta do Ollama API: {response.text}")

        # Processa as respostas em múltiplas linhas
        response_lines = response.text.strip().splitlines()
        full_response = ""
        
        for line in response_lines:
            try:
                # Tenta interpretar cada linha como JSON usando json.loads
                data = json.loads(line)  # Usa json.loads para analisar a linha
                if "response" in data:
                    full_response += data["response"]
                if data.get("done"):
                    break  # Para se a resposta estiver completa
            except ValueError as e:
                logger.error(f"Erro ao processar linha JSON: {line}, erro: {e}")

        if full_response:
            return {"response": full_response.strip()}
        else:
            logger.error("Nenhuma resposta válida foi recebida do Ollama API.")
            raise HTTPException(status_code=500, detail="Nenhuma resposta válida recebida.")

    except httpx.RequestError as e:
        logger.exception("Erro de conexão ao acessar o Ollama API.")
        raise HTTPException(status_code=500, detail="Erro de conexão com o Ollama API.")

    except Exception as e:
        logger.exception("Erro desconhecido ao processar a solicitação.")
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")

# Endpoint OPTIONS para evitar erros CORS no frontend
@app.options("/chat/")
async def options_chat():
    return {"detail": "OK"}
