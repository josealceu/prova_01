import json, os, threading, datetime
from flask import Flask, request, jsonify
import redis, pika

# ------------- Redis -----------------
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
CACHE_KEY = "eventos_cache"

# ------------- Flask -----------------
app = Flask(__name__)
eventos = []   # memória local

@app.post('/evento')
def post_evento():
    data = request.get_json(force=True)
    eventos.append(data)
    r.set(CACHE_KEY, json.dumps(eventos))
    return {"saved": True}, 201

@app.get('/eventos')
def get_eventos():
    cached = r.get(CACHE_KEY)
    return jsonify(json.loads(cached) if cached else eventos)

# ------------- RabbitMQ consumer -----
def consume_rabbit():
    conn = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBIT_HOST","rabbitmq")))
    ch   = conn.channel()
    ch.queue_declare(queue='logistics')

    def cb(_ch, _method, _props, body):
        eventos.append({
            "type": "logistics",
            "payload": json.loads(body.decode()),
            "when": datetime.datetime.utcnow().isoformat()
        })
        r.set(CACHE_KEY, json.dumps(eventos))

    ch.basic_consume(queue='logistics', on_message_callback=cb, auto_ack=True)
    ch.start_consuming()

if __name__ == '__main__':
    threading.Thread(target=consume_rabbit, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
