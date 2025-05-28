import 'dotenv/config';
import express from 'express';
import Redis from 'ioredis';
import axios from 'axios';

const app = express();
app.use(express.json());

const redis = new Redis({ host: process.env.REDIS_HOST, port: 6379 });
const CACHE_KEY = 'sensor_cache';
const TTL = 30;          // segundos

app.get('/sensor-data', async (_, res) => {
  const cached = await redis.get(CACHE_KEY);
  if (cached) return res.json(JSON.parse(cached));

  // gera medições simuladas
  const data = {
    timestamp: new Date().toISOString(),
    temperature: (70 + Math.random() * 10).toFixed(2) + ' °C',
    pressure: (2000 + Math.random() * 200).toFixed(0) + ' psi'
  };

  await redis.set(CACHE_KEY, JSON.stringify(data), 'EX', TTL);
  res.json(data);
});

app.post('/alert', async (req, res) => {
  const payload = { ...req.body, source: 'sensor-api', when: new Date().toISOString() };
  try {
    await axios.post(process.env.EVENTS_URL, payload);
    res.status(202).json({ ok: true });
  } catch (err) {
    res.status(502).json({ error: err.message });
  }
});

app.listen(3000, () => console.log('Sensors API running on :3000'));
