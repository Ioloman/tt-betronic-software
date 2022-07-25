docker-compose up -d postgres redis rabbitmq
bash wait-for-it.sh localhost:5432 -s -t 0 -- echo "Postgres is up"
bash wait-for-it.sh localhost:6379 -s -t 0 -- echo "Redis is up"
bash wait-for-it.sh localhost:5672 -s -t 0 -- echo "RabbitMQ is up but need to wait" && sleep 5
docker-compose up -d line-provider bet-maker