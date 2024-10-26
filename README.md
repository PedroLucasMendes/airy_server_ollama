# airy_server_ollama

O script foi desenvolvido para fazer um benchmarking na API direta do Ollama

Caso utilize placa de vídeo nvidia, baixar o software NVIDIA CUDA;

Script desenvolvido para o llama3.2:1b, trocar caso necessário;

# Lib necessárias
pip install uvicorn fastapi httpx psutil gputil

# Terminal 1
python -m http.server 8080

# Terminal 2
uvicorn app:app --reload --port 8000

# Terminal 3
python stress.py
