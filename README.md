# Тестовое задание Middle Python Developer

Ссылки на репозитории:
 - [tt-bet-maker](https://github.com/Ioloman/tt-bet-maker)
 - [tt-line-provider](https://github.com/Ioloman/tt-line-provider)

Запуск (времени не хватило добавить `wait-for-it.sh`):
- `docker-compose up -d postgres redis rabbitmq`
- `docker-compose up -d line-provider bet-maker`

line-provider - 8005 порт
bet-maker - 8006 порт

P. S. Также у сервиса bet-maker отсутствуют комментарии и тесты, 
так как заканчивал в спешке.
Добавлю по возможности как можно быстрее. (может быть это никто и не увидит)