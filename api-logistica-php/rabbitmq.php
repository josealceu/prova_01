<?php
require 'vendor/autoload.php';
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

function publish($msg) {
  $host = getenv("RABBIT_HOST") ?: "rabbitmq";
  $connection = new AMQPStreamConnection($host, 5672, 'guest', 'guest');
  $channel    = $connection->channel();
  $channel->queue_declare('logistica', false, false, false, false);
  $channel->basic_publish(new AMQPMessage($msg), '', 'logistica');
  $channel->close();
  $connection->close();
}
