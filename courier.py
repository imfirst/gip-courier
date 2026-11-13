#!/usr/bin/env python3
"""Курьер ГИП-бота: GitHub Actions <-> Telegram <-> gipproekt.ru/crm/relay.php.
Хостинг не видит api.telegram.org, поэтому сообщения возит этот скрипт.
Работает ~4.5 минуты: каждые ~25 секунд забирает новые сообщения из Telegram,
передаёт их на сайт и отправляет в Telegram то, что сайт поставил в очередь."""
import json, os, time, urllib.request, urllib.error

TOKEN = os.environ['BOT_TOKEN']
RELAY = os.environ['RELAY_URL']          # https://gipproekt.ru/crm/relay.php
KEY = os.environ['CRM_KEY']              # api_key из config.php
RUN_SECONDS = int(os.environ.get('RUN_SECONDS', '270'))
TG = os.environ.get('TG_BASE', 'https://api.telegram.org') + f'/bot{TOKEN}/'


def post(url, data, headers=None, timeout=40):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST',
                                 headers={'Content-Type': 'application/json', **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8') or '{}')
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode('utf-8') or '{}')
        except Exception:
            return {'ok': False, 'error_code': e.code}


def site(op, **extra):
    return post(RELAY, {'op': op, **extra}, {'X-CRM-Key': KEY, 'User-Agent': 'gip-courier'})


def tg(method, payload, timeout=40):
    return post(TG + method, payload, timeout=timeout)


def main():
    start = time.time()
    tg('deleteWebhook', {})            # getUpdates не работает, если висит вебхук
    while time.time() - start < RUN_SECONDS:
        try:
            offset = int(site('pull').get('offset', 0))
            left = RUN_SECONDS - (time.time() - start)
            wait = max(0, min(25, int(left) - 5))
            r = tg('getUpdates', {'offset': offset, 'timeout': wait,
                                  'allowed_updates': ['message', 'callback_query']}, timeout=wait + 15)
            updates = r.get('result', []) if r.get('ok') else []
            if r.get('ok') is False:
                print('getUpdates:', r.get('description'))
            res = site('push', updates=updates)
            if not res.get('ok'):
                print('relay error:', res)
                time.sleep(10)
                continue
            for item in res.get('outbox', []):
                s = tg(item['method'], item['payload'])
                if not s.get('ok'):
                    print('send failed:', item['method'], s.get('description'))
            if updates or res.get('outbox'):
                print(f"updates={len(updates)} sent={len(res.get('outbox', []))}")
        except Exception as e:                # сеть мигнула — пробуем дальше
            print('error:', e)
            time.sleep(10)


if __name__ == '__main__':
    main()
