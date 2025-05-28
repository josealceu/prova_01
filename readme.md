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
git clone <repo>
cd oil-system
docker compose up -d            # levanta tudo