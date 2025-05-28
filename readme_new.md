# Integração de APIs – Setor de Petróleo  
*(visão funcional resumida)*

---

## 1 ▪ O que cada API faz & como executá-la

| Serviço (porta) | Linguagem | Comando local | Objetivo funcional |
|-----------------|-----------|---------------|--------------------|
| **sensors-api** (3000) | Node.js 18 | `node app.js` <br>ou `npm start` | • Gera leituras **simuladas** de temperatura / pressão (`GET /sensor-data`).<br>• Dispara **alertas** para a API Python (`POST /alert`). |
| **events-api** (5000)  | Python 3.11 | `python app.py` | • **Recebe** alertas via HTTP (`POST /event`).<br>• **Consome** mensagens de logística vindas da fila RabbitMQ.<br>• Entrega histórico consolidado (`GET /events`). |
| **logistics-api** (8000) | PHP 8.1 | `php -S 0.0.0.0:8000` | • Lista **equipamentos** simulados (`GET /equipments`).<br>• Publica **despachos urgentes** na fila RabbitMQ (`POST /dispatch`). |

> **Execução em Docker:**  
> ```bash
> docker compose up -d      # sobe Redis, RabbitMQ e as três APIs
> ```

---

## 2 ▪ Como as APIs se comunicam


* **Passo 1 – Síncrono:** `POST /alert` envia JSON direto do Node para o Python.  
* **Passo 2 – Assíncrono:** PHP publica despachos na fila **logistics** do RabbitMQ.  
* **Passo 3 – Consumo:** consumidor em `events-api` lê cada mensagem e armazena como novo evento.

---

## 3 ▪ Onde o Redis é usado

| API | Chave | Conteúdo armazenado | TTL |
|-----|-------|--------------------|-----|
| **sensors-api** | `sensor_cache` | última leitura simulada | 30 s |
| **events-api**  | `events_cache` | lista JSON com todos os eventos (alertas + despachos) | sem TTL (sobrescreve a cada mudança) |

Redis garante resposta rápida e reduz processamento repetido.

---

## 4 ▪ Como a fila RabbitMQ entra no fluxo

1. **Usuário** chama `POST /dispatch` em **logistics-api**.  
2. PHP cria a mensagem (JSON) e **publica** na fila `logistics`.  
3. **events-api** mantém um **consumidor** permanente; quando a mensagem chega, ela é lida, convertida em objeto Python e adicionada ao histórico de eventos.  
4. Qualquer acesso a `GET /events` mostrará tanto os **alertas** (HTTP) quanto os **despachos** (RabbitMQ).

*Interface de administração:* http://localhost:15672  
(login padrão: guest / guest)  
Ali é possível ver a fila crescendo e esvaziando em tempo real.

---

> **Teste rápido**

```bash
# Gera leitura e coloca em cache
curl localhost:3000/sensor-data

# Dispara alerta via HTTP
curl -X POST localhost:3000/alert -H "Content-Type: application/json" -d '{"msg":"Pressão alta"}'

# Publica despacho via RabbitMQ
curl -X POST localhost:8000/dispatch -H "Content-Type: application/json" -d '{"equipment":"válvula","priority":"high"}'

# Confere eventos consolidados
curl localhost:5000/events
