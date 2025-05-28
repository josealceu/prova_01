import json, os, threading, datetime
from flask import Flask, request, jsonify
import redis, pika

# ------------- Redis -----------------
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
CACHE_KEY = "events_cache"

# ------------- Flask -----------------
app = Flask(__name__)
events = []   # memória local

@app.post('/event')
def post_event():
    data = request.get_json(force=True)
    events.append(data)
    r.set(CACHE_KEY, json.dumps(events))
    return {"saved": True}, 201

@app.get('/events')
def get_events():
    cached = r.get(CACHE_KEY)
    return jsonify(json.loads(cached) if cached else events)

# ------------- RabbitMQ consumer -----
def consume_rabbit():
    conn = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBIT_HOST","rabbitmq")))
    ch   = conn.channel()
    ch.queue_declare(queue='logistics')

    def cb(_ch, _method, _props, body):
        events.append({
            "type": "logistics",
            "payload": json.loads(body.decode()),
            "when": datetime.datetime.utcnow().isoformat()
        })
        r.set(CACHE_KEY, json.dumps(events))

    ch.basic_consume(queue='logistics', on_message_callback=cb, auto_ack=True)
    ch.start_consuming()

if __name__ == '__main__':
    threading.Thread(target=consume_rabbit, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
