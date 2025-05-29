<?php
require 'rabbitmq.php';

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
header('Content-Type: application/json');

if ($path === '/equipamentos') {
  echo json_encode([
    ['id'=>1,'name'=>'Bomba de Submersão'],
    ['id'=>2,'name'=>'Válvula de Alta Pressão'],
    ['id'=>3,'name'=>'Guindaste Móvel']
  ]);
}
elseif ($path === '/dispatch' && $_SERVER['REQUEST_METHOD'] === 'POST') {
  $body = file_get_contents('php://input');
  publish($body ?: '{"alerta":"dispatch"}');
  echo json_encode(['queued'=>true]);
}
else {
  http_response_code(404);
  echo json_encode(['error'=>'not found']);
}
