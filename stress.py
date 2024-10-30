import requests
import threading
import time
import statistics
import json
import psutil  # Para medir a utilização da CPU
import GPUtil  # Para medir a utilização da GPU
import csv  # Para gerar arquivos CSV

# URL da API
API_URL = "http://localhost:11434/api/generate"

# Listas para armazenar os dados
response_times = []
tokens_per_second = []
tokens_per_response = []
cpu_usages = []  # Armazena o uso médio da CPU por requisição
gpu_usages = []  # Armazena o uso médio da GPU por requisição

# Função para monitorar continuamente CPU e GPU durante a requisição
def monitor_usage(stop_event, cpu_usage_list, gpu_usage_list):
    while not stop_event.is_set():
        cpu_usage_list.append(psutil.cpu_percent(interval=None))  # Uso atual da CPU
        gpu_usage = GPUtil.getGPUs()[0].load * 100 if GPUtil.getGPUs() else 0  # Uso atual da GPU
        gpu_usage_list.append(gpu_usage)
        time.sleep(0.1)  # Intervalo de 100ms entre as medições

# Função para enviar requisições à API e medir o desempenho
def send_request(prompt):
    start_time = time.time()  # Marca o tempo inicial da requisição

    # Preparação do monitoramento de CPU e GPU
    cpu_usage_list = []
    gpu_usage_list = []
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_usage, args=(stop_event, cpu_usage_list, gpu_usage_list))
    monitor_thread.start()  # Inicia o monitoramento

    try:
        response = requests.post(API_URL, json={"model": "llama3.2:1b", "prompt": prompt}, stream=True)
        

        full_response = ""  # Variável para armazenar a resposta completa

        # Lê a resposta linha por linha
        for line in response.iter_lines():
            if line:
                try:
                    json_line = line.decode('utf-8')  # Decodifica a linha
                    data = json.loads(json_line)  # Converte a linha para JSON

                    if "response" in data:
                        full_response += data["response"]  # Concatena a resposta
                        if data.get("done"):
                            break  # Para quando a resposta estiver completa
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")

        end_time = time.time()  # Tempo ao receber a resposta completa
        response_time = end_time - start_time  # Tempo total de resposta
        response_times.append(response_time)  # Armazena o tempo de resposta

        # Calcula e armazena tokens gerados
        tokens = len(full_response.split())
        tokens_per_response.append(tokens)
        tokens_per_second.append(tokens / response_time if response_time > 0 else 0)

    except Exception as e:
        print(f"Erro ao enviar requisição: {e}")

    finally:
        # Para o monitoramento e aguarda o término do thread
        stop_event.set()
        monitor_thread.join()

        # Calcula a média de uso da CPU e GPU durante a requisição
        avg_cpu_usage = statistics.mean(cpu_usage_list) if cpu_usage_list else 0
        avg_gpu_usage = statistics.mean(gpu_usage_list) if gpu_usage_list else 0

        cpu_usages.append(avg_cpu_usage)
        gpu_usages.append(avg_gpu_usage)

        print(f"Prompt: {prompt}, Tempo de Resposta: {response_time:.2f}s, Tokens: {tokens}, "
              f"CPU Média: {avg_cpu_usage:.2f}%, GPU Média: {avg_gpu_usage:.2f}%")

# Lista de perguntas
perguntas = [
    "Quais são as principais causas da mudança climática e como elas impactam o meio ambiente?",
    "Como a inteligência artificial está transformando a indústria de saúde e quais são os desafios éticos associados?",
    "Quais são os efeitos da globalização na cultura local e como isso pode ser observado em diferentes partes do mundo?",
    "Qual é a história e a evolução da música clássica, e como ela influenciou outros gêneros musicais?",
    "Como as redes sociais mudaram a maneira como as pessoas se comunicam e interagem socialmente?",
    "Quais são os avanços mais significativos na exploração espacial nos últimos 50 anos e qual é o futuro da exploração espacial?",
    "Como a literatura reflete as questões sociais e políticas de sua época, e quais são alguns exemplos notáveis?",
    "Quais são os principais componentes do sistema econômico global e como eles interagem entre si?",
    "Como a educação pode ser reformulada para atender às necessidades do século XXI, considerando a tecnologia e as habilidades do futuro?",
    "Quais são os benefícios e desafios da energia renovável em comparação com as fontes de energia tradicionais?",
    "Como a filosofia ocidental evoluiu ao longo dos séculos e quais pensadores tiveram o maior impacto?",
    "Quais são os impactos psicológicos da pandemia de COVID-19 na sociedade e como as pessoas estão lidando com isso?",
    "Como a arte contemporânea reflete as questões sociais e políticas atuais e quais são alguns exemplos impactantes?",
    "Quais são os efeitos da dieta moderna na saúde e bem-estar das pessoas, e como isso se compara a dietas tradicionais?",
    "Como a tecnologia está mudando o mercado de trabalho e quais habilidades serão mais valorizadas no futuro?",
    "Quais são os desafios enfrentados pelas democracias modernas e como eles afetam a política global?",
    "Como a história da ciência moldou nosso entendimento do mundo e quais são algumas descobertas revolucionárias?",  
    "Quais são os principais fatores que contribuem para a desigualdade social e econômica, e como podemos abordá-los?",
    "Como a narrativa e a estrutura dos filmes evoluíram ao longo do tempo e quais são as tendências atuais?",
    "Quais são os impactos ambientais da agricultura industrial e quais alternativas sustentáveis existem?"
]

# Função principal para executar as requisições em threads
def main():
    threads = []
    for prompt in perguntas:
        thread = threading.Thread(target=send_request, args=(prompt,))
        threads.append(thread)
        thread.start()

    # Aguarda a conclusão de todas as threads
    for thread in threads:
        thread.join()

    # Cálculo das métricas finais
    average_response_time = statistics.mean(response_times) if response_times else 0
    average_tokens_per_second = statistics.mean(tokens_per_second) if tokens_per_second else 0
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    total_tokens = sum(tokens_per_response) if tokens_per_response else 0

    # Exibe as métricas
    print(f"\nMédia do tempo de resposta: {average_response_time:.2f}s")
    print(f"Média de tokens por segundo: {average_tokens_per_second:.2f} tokens/s")
    print(f"Tempo máximo de resposta: {max_response_time:.2f}s")
    print(f"Tempo mínimo de resposta: {min_response_time:.2f}s")
    print(f"Total de tokens gerados: {total_tokens}")

    # Gera um arquivo CSV com os resultados
    with open('resultados_requisicoes.csv', mode='w', newline='') as csv_file:
        fieldnames = ['Prompt', 'Tempo de Resposta', 'Tokens', 'Tokens por Segundo',
                      'CPU Média (%)', 'GPU Média (%)', 'Média do Tempo de Resposta',
                      'Média de Tokens por Segundo', 'Tempo Máximo de Resposta',
                      'Tempo Mínimo de Resposta', 'Total de Tokens']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for prompt, response_time, tokens, cpu_usage, gpu_usage in zip(
                perguntas, response_times, tokens_per_response, cpu_usages, gpu_usages):
            writer.writerow({
                'Prompt': prompt,
                'Tempo de Resposta': response_time,
                'Tokens': tokens,
                'Tokens por Segundo': tokens / response_time if response_time > 0 else 0,
                'CPU Média (%)': cpu_usage,
                'GPU Média (%)': gpu_usage,
                'Média do Tempo de Resposta': average_response_time,
                'Média de Tokens por Segundo': average_tokens_per_second,
                'Tempo Máximo de Resposta': max_response_time,
                'Tempo Mínimo de Resposta': min_response_time,
                'Total de Tokens': total_tokens
            })

if __name__ == "__main__":
    main()
