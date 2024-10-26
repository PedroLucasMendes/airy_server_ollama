# airy_server_ollama

O script foi desenvolvido para fazer um benchmarking na API direta do Ollama

Caso utilize placa de vídeo nvidia, baixar o software NVIDIA CUDA;

Script desenvolvido para o llama3.2:1b, trocar caso necessário;

Para baixar o ollama, acesse o seguinte link:

https://ollama.com/download

Para instalar o modelo:

* Acessar o powershell e digitar o seguinte comando:

ollama pull llama3.2:1b

* Digite o seguinte comando apenas por garantia para abrir o server

ollama serve

# Lib necessárias
pip install uvicorn fastapi httpx psutil gputil

# Terminal 1
python -m http.server 8080

# Terminal 2
uvicorn app:app --reload --port 8000

# Terminal 3
python stress.py
