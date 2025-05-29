# Prova integração de APIs, serviços para Petróleo  


Aplicação está em Docker:

> **Execução em Docker:**  
> ```bash
> docker compose up -d 
> ``


| Micro Serviço | Linguagem Utilizada | Comando  para rodar | Objetivo |
|-----------------|-----------|---------------|--------------------|
| **sensors-api** (3000). | Node.js |`npm start (Comando do Dockerfile)` | • Faz leituras **simuladas** de temperatura e de pressão (`GET /sensor-data`).<br>• Encaminha um  **alerta** para a API Python no end-point (`POST /alerta`). |
| **eventos-api** (5000)  | Python| `python app.py(Comando do Dockerfile)` | • **Recebe** alertas por meio de HTTP (`POST /evento`).<br>• **Consome** texto de logística que veio da fila RabbitMQ.<br>• manda o  histórico (`GET /eventos`). |
| **logistica-api** (8000) | PHP | `php -S 0.0.0.0:8000 (Comando do Dockerfile)` | • Lista **equipamentos** simulados (`GET /equipamentos`).<br>• Publica **despachos urgentes** na fila RabbitMQ (`POST /dispatch`). |


## 1 ▪ O que cada API faz & como executá-la

| Serviço | Linguagem Utilizada | Comando para rodar | Objetivo |

|-----------------|-----------|---------------|--------------------|

| sensors-api (3000) | Node.js |npm start (Comando do Dockerfile) | Faz leituras simuladas de temperatura / pressão (GET /sensor-data); manda alertas para a API Python (POST /alerta) |

| eventos-api (5000) | Python| python app.py(Comando do Dockerfile) | Recebe alertas via HTTP (POST /evento); Consome texto de logística que veio da fila RabbitMQ; manda o histórico (GET /eventos) |

| logistica-api (8000) | PHP | php -S 0.0.0.0:8000 (Comando do Dockerfile) | Lista equipamentos simulados (GET /equipamentos); publica despachos urgentes na fila RabbitMQ (POST /dispatch) |


---

## 2 ▪ Como as APIs se comunicam


* **Passo 1 – Comunicação Síncrono:** na rota `POST /alerta` encaminha um JSON do Node para o Python.  
* **Passo 2 – Comunicação Assíncrono:** PHP manda na fila **logistica** do RabbitMQ.  
* **Passo 3 – Consumo:** Consome os dados em `eventos-api` ao qual lê cada mensagem e armazena como novo evento.

---

## 3 ▪ Onde o Redis é usado

| API | Chave | Conteúdo armazenado | TTL |
|-----|-------|--------------------|-----|
| **sensors-api** | `sensor_cache` | é uma leitura simulada | 30 s |
| **eventos-api**  | `eventos_cache` | Ele lista os JSONs com  os eventoos "alertas e despachos" | sem TTL (sobrescreve a cada uma das mudança) |

---

## 4 ▪ Como a fila RabbitMQ Atua dentro do nosso fluxo

1. **Usuário final** chama o end-point `POST /dispatch` no microserviço **logistica-api**.  
2. O PHP cria uma mensagem em JSON e após isto **publica** na fila `logistica`.  
3. **eventos-api** mantém também um **consumidor** permanente aqui; quando a mensagem chega, ela é lida, e logo após convertida em objeto Python e inserida ao histórico de eventos.  
4. Qualquer modo de acesso ao end-point `GET /eventos` será possível visualizar tanto os **alertas** (HTTP) quanto os despachos (RabbitMQ).

*Interface RabbirMq é acessível pela URL:* http://localhost:15672
(login utilizado foi o padrão: guest / guest)  


---

> **Testes dos end-points**

```bash
# neste EndPoint ele Gera uma leitura e coloca ela em cache com redis
curl localhost:3000/sensor-data



# este EndPoint ele Dispara alerta por meio de HTTP para o microserviço em Python
curl -X POST localhost:3000/alerta -H "Content-Type: application/json" -d '{"msg":"Pressão está muito alta"}'




# este EndPoint ele Publica via Rabiitmq 
curl -X POST localhost:8000/dispatch -H "Content-Type: application/json" -d '{"equipment":"Válvula","priority":"Alta"}'




# este EndPoint é possível visualizar os eventos
curl localhost:5000/eventos
