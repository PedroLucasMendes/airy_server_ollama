# airy_server_ollama

Caso utilize placa de vídeo nvidia, baixar o software NVIDIA CUDA;
Script desenvolvido para o llama3.2:1b, trocar caso necessário;

pip install uvicorn fastapi httpx

# Terminal 1
python -m http.server 8080

# Terminal 2
uvicorn app:app --reload --port 8000

# Terminal 3
python stress.py
