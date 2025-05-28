FROM php:8.1-cli

WORKDIR /app

# 1) Dependências de sistema mínimas para compilar extensões e usar Composer
RUN apt-get update \
 && apt-get install -y --no-install-recommends git unzip zip \
 # 2) Habilita a extensão sockets (requerida pelo php-amqplib)
 && docker-php-ext-install sockets \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3) Instala o Composer
RUN curl -sS https://getcomposer.org/installer \
 | php -- --install-dir=/usr/bin --filename=composer

# 4) Copia definição de dependências
COPY composer.json composer.lock* ./

# 5) Instala libs sem dev
RUN composer install --no-dev --prefer-dist --no-progress --no-interaction

# 6) Copia o código-fonte
COPY . .

EXPOSE 8000
CMD ["php","-S","0.0.0.0:8000","index.php"]
