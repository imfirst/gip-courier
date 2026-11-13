# Курьер ГИП-бота на GitHub Actions

Хостинг ihc.ru не видит api.telegram.org. Курьер на серверах GitHub каждые ~5 минут
(внутри — каждые 25 секунд) забирает сообщения из Telegram, отдаёт их сайту
(gipproekt.ru/crm/relay.php) и отправляет в Telegram ответы, которые сайт поставил в очередь.
Задержка ответа бота — обычно до минуты, иногда до 10–15 минут (GitHub не всегда запускает вовремя).

## Установка (10 минут)
1. github.com → New repository → имя `gip-courier` → **Public** (публичный: у GitHub на публичных
   репозиториях Actions бесплатны без лимита минут; в коде нет ни паролей, ни токенов).
2. Загрузите в репозиторий файлы из этой папки так, чтобы было:
   `courier.py` и `.github/workflows/courier.yml`
   (Add file → Upload files; папку .github проще создать через Add file → Create new file,
   вписав имя `.github/workflows/courier.yml` и вставив текст).
3. Settings → Secrets and variables → Actions → New repository secret, три штуки:
   - `BOT_TOKEN` — токен @giphelp_bot
   - `CRM_KEY` — тот же api_key, что в config.php
   - `RELAY_URL` — `https://gipproekt.ru/crm/relay.php`
4. Вкладка Actions → gip-courier → Run workflow (первый запуск вручную).
   Через минуту напишите боту /start — он ответит.

## Важно
- Если в репозитории 60 дней ничего не меняется, GitHub приостанавливает запуски по расписанию
  и присылает письмо. Тогда: Actions → gip-courier → Enable workflow (или поправить любой файл).
- Логи: Actions → любой запуск → Run courier.
