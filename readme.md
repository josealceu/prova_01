# Integração de APIs – Operação de Petróleo (Docker Compose)

## 1. O que cada API faz & como executar
| Serviço (porta) | Linguagem | Comando interno | Função resumida |
|-----------------|-----------|-----------------|-----------------|
| **sensors-api** (3000) | Node.js 18 | `node app.js` | Simula leitura de **temperatura** e **pressão**; dispara alertas. |
| **events-api**  (5000) | Python 3.11 | `python app.py` | Armazena todos os **eventos** (HTTP + fila). |
| **logistics-api** (8000) | PHP 8.1 | `php -S 0.0.0.0:8000` | Lista equipamentos e envia **despachos** para logística (RabbitMQ). |
| **redis** (6379) | imagem oficial | – | Cache in-memory usado por Node e Python. |
| **rabbitmq** (5672 / 15672) | imagem oficial | – | Mensageria assíncrona; UI em http://localhost:15672 (guest/guest). |

**Executar:**  
```bash

é necessário ter a Stack do Docker e Docker Compose instalado no computador. Acessar o diretório e rodar:
| **docker compose up -d**          





Síncrono (HTTP) – POST /alert do Node envia direto para POST /event do Python.

Assíncrono (RabbitMQ) – POST /dispatch do PHP publica na fila logistics; Python consome em segundo plano e converte em evento # levanta tudo




onde é usado:

3. Onde o Redis é usado
API	Chave	Conteúdo	TTL
Node (sensors-api)	sensor_cache	última medição simulada	30 s
Python (events-api)	events_cache	lista JSON de todos os eventos	substituído a cada alteração


--------------------------------------------------

Como a fila RabbitMQ entra no fluxo.

POST /dispatch → PHP cria mensagem JSON.

Mensagem cai na fila logistics (RabbitMQ).

events-api (Python) roda um consumidor que, ao receber a mensagem, salva-a na lista de eventos.

Qualquer GET /events mostrará tanto alertas quanto despachos.