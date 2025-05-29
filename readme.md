# Prova integração de APIs, serviços para Petróleo  


Aplicação está em Docker

> **Execução em Docker:**  
> ```bash
> docker compose up -d 
> ``

## 1 ▪ O que cada API faz & como executá-la

| Serviço | Linguagem Utilizada | Comando  para rodar | Objetivo |
|-----------------|-----------|---------------|--------------------|
| **sensors-api** (3000) | Node.js |`npm start (Comando do Dockerfile)` | • Faz leituras **simuladas** de temperatura / pressão (`GET /sensor-data`).<br>• manda **alertas** para a API Python (`POST /alerta`). |
| **eventos-api** (5000)  | Python| `python app.py(Comando do Dockerfile)` | • **Recebe** alertas via HTTP (`POST /evento`).<br>• **Consome** texto de logística que veio da fila RabbitMQ.<br>• manda o  histórico (`GET /eventos`). |
| **logistica-api** (8000) | PHP | `php -S 0.0.0.0:8000 (Comando do Dockerfile)` | • Lista **equipamentos** simulados (`GET /equipamentos`).<br>• Publica **despachos urgentes** na fila RabbitMQ (`POST /dispatch`). |

`

---

## 2 ▪ Como as APIs se comunicam


* **Passo 1 – Síncrono:** `POST /alerta` envia JSON do Node para o Python.  
* **Passo 2 – Assíncrono:** PHP publica na fila **logistica** do RabbitMQ.  
* **Passo 3 – Consumo:** consumidor em `eventos-api` lê cada mensagem e armazena como novo evento.

---

## 3 ▪ Onde o Redis é usado

| API | Chave | Conteúdo armazenado | TTL |
|-----|-------|--------------------|-----|
| **sensors-api** | `sensor_cache` | última leitura simulada | 30 s |
| **eventos-api**  | `eventos_cache` | lista os JSON com todos os eventoos (alertas + despachos) | sem TTL (sobrescreve a cada mudança) |

---

## 4 ▪ Como a fila RabbitMQ entra no fluxo

1. **Usuário** chama `POST /dispatch` em **logistica-api**.  
2. PHP cria mensagem (JSON) e **publica** na fila `logistica`.  
3. **eventos-api** mantém um **consumidor** permanente; quando a mensagem chega, é lida, convertida em objeto Python e adicionada ao histórico de eventoos.  
4. Qualquer acesso a `GET /eventos` mostrará tanto os **alertaas** (HTTP) quanto os despachos (RabbitMQ).

*Interface RabbirMq:* http://localhost:15672
(login padrão: guest / guest)  


---

> **Testes rápido**

```bash
# Gera leitura e coloca em cache
curl localhost:3000/sensor-data



# Dispara alertaa via HTTP para Python
curl -X POST localhost:3000/alerta -H "Content-Type: application/json" -d '{"msg":"Pressão está alta"}'




# Publica via Rabiitmq
curl -X POST localhost:8000/dispatch -H "Content-Type: application/json" -d '{"equipment":"Válvula","priority":"Alta"}'




# Confere eventoos
curl localhost:5000/eventos
