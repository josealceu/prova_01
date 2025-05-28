# Integração de APIs – Setor de Petróleo  

> **Execução em Docker:**  
> ```bash
> docker compose up -d 
> ``

## 1 ▪ O que cada API faz & como executá-la

| Serviço (porta) | Linguagem | Comando local | Objetivo funcional |
|-----------------|-----------|---------------|--------------------|
| **sensors-api** (3000) | Node.js |`npm start (Comando do Dockerfile)` | • Faz leituras **simuladas** de temperatura / pressão (`GET /sensor-data`).<br>• manda **alertas** para a API Python (`POST /alert`). |
| **events-api** (5000)  | Python 3.11 | `python app.py(Comando do Dockerfile)` | • **Recebe** alertas via HTTP (`POST /event`).<br>• **Consome** texto de logística que veio da fila RabbitMQ.<br>• manda o  histórico (`GET /events`). |
| **logistics-api** (8000) | PHP 8.1 | `php -S 0.0.0.0:8000 (Comando do Dockerfile)` | • Lista **equipamentos** simulados (`GET /equipments`).<br>• Publica **despachos urgentes** na fila RabbitMQ (`POST /dispatch`). |

`

---

## 2 ▪ Como as APIs se comunicam


* **Passo 1 – Síncrono:** `POST /alert` envia JSON do Node para o Python.  
* **Passo 2 – Assíncrono:** PHP publica despachos na fila **logistics** do RabbitMQ.  
* **Passo 3 – Consumo:** consumidor em `events-api` lê cada mensagem e armazena como novo evento.

---

## 3 ▪ Onde o Redis é usado

| API | Chave | Conteúdo armazenado | TTL |
|-----|-------|--------------------|-----|
| **sensors-api** | `sensor_cache` | última leitura simulada | 30 s |
| **events-api**  | `events_cache` | lista JSON com todos os eventos (alertas + despachos) | sem TTL (sobrescreve a cada mudança) |

---

## 4 ▪ Como a fila RabbitMQ entra no fluxo

1. **Usuário** chama `POST /dispatch` em **logistics-api**.  
2. PHP cria mensagem (JSON) e **publica** na fila `logistics`.  
3. **events-api** mantém um **consumidor** permanente; quando a mensagem chega, é lida, convertida em objeto Python e adicionada ao histórico de eventos.  
4. Qualquer acesso a `GET /events` mostrará tanto os **alertas** (HTTP) quanto os **despachos** (RabbitMQ).

*Interface de administração:* http://localhost:15672  
(login padrão: guest / guest)  


---

> **Testes rápido**

```bash
# Gera leitura e coloca em cache
curl localhost:3000/sensor-data



# Dispara alerta via HTTP para Python
curl -X POST localhost:3000/alert -H "Content-Type: application/json" -d '{"msg":"Pressão está alta"}'




# Publica via Rabiitmq
curl -X POST localhost:8000/dispatch -H "Content-Type: application/json" -d '{"equipment":"Válvula","priority":"Alta"}'




# Confere eventos
curl localhost:5000/events
