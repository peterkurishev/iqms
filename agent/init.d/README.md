sudo chmod +x /etc/init.d/internet-monitor-agent
sudo update-rc.d internet-monitor-agent defaults


Чтобы агент для мониторинга интернета автоматически запускался при
старте Linux, лучше всего создать systemd-сервис. Вот пошаговая
инструкция:

### 1. Создаем сервисный файл
Создайте файл сервиса в `/etc/systemd/system/internet-monitor-agent.service`:

```ini
[Unit]
Description=Internet Quality Monitoring Agent
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/internet-monitor-agent
ExecStart=/usr/bin/python3 /opt/internet-monitor-agent/agent.py
EnvironmentFile=/etc/default/internet-monitor-agent
Restart=always
RestartSec=30
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=net-monitor-agent

# Защита сервиса
ProtectSystem=full
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

### 2. Создаем конфигурационный файл для переменных окружения
Создайте файл конфигурации `/etc/default/internet-monitor-agent`:

```bash
# API endpoint сервера
API_URL="https://iqms.vsdg.ru/api"

# Секретный ключ агента
API_KEY="your_agent_secret_key"

# Интервал измерений в секундах (1800 = 30 минут)
MEASUREMENT_INTERVAL=1800

# Дополнительные параметры
TEST_SERVER_AUTO_SELECT=true
LOG_LEVEL="INFO"
```

### 3. Размещаем код агента
Рекомендуемая структура каталогов:
```
/opt/internet-monitor-agent/
├── agent.py             # основной скрипт
├── requirements.txt     # зависимости Python
└── utils/               # вспомогательные модули
    ├── network_tests.py
    └── config_loader.py
```

### 4. Устанавливаем зависимости
```bash
sudo pip3 install -r /opt/internet-monitor-agent/requirements.txt
```

### 5. Активируем сервис
```bash
# Перезагружаем демон systemd
sudo systemctl daemon-reload

# Включаем автозагрузку
sudo systemctl enable internet-monitor-agent

# Запускаем сервис
sudo systemctl start internet-monitor-agent
```

### 6. Управление сервисом
```bash
# Проверка статуса
sudo systemctl status internet-monitor-agent

# Просмотр логов
journalctl -u internet-monitor-agent -f

# Перезапуск сервиса
sudo systemctl restart internet-monitor-agent

# Остановка сервиса
sudo systemctl stop internet-monitor-agent
```

### Дополнительные настройки

**Для работы с Python-окружением:**
Если используете virtualenv, измените `ExecStart` в сервисном файле:
```ini
ExecStart=/opt/internet-monitor-agent/venv/bin/python /opt/internet-monitor-agent/agent.py
```

**Автоматическое восстановление:**
Параметры `Restart=always` и `RestartSec=30` гарантируют, что агент перезапустится при:
- Любом завершении (кроме остановки через systemctl)
- Крахе процесса
- Ошибке запуска
- Ненулевом коде возврата

**Безопасность:**
- `ProtectSystem=full` - защищает системные файлы
- `PrivateTmp=true` - изолированные временные файлы
- `NoNewPrivileges=true` - запрет повышения привилегий

### Для систем без systemd (SysVinit)
Создайте скрипт в `/etc/init.d/internet-monitor-agent`:
```bash
#!/bin/sh
### BEGIN INIT INFO
# Provides:          internet-monitor-agent
# Required-Start:    $network $remote_fs $syslog
# Required-Stop:     $network $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
### END INIT INFO

DAEMON="/usr/bin/python3 /opt/internet-monitor-agent/agent.py"
PIDFILE="/var/run/internet-monitor-agent.pid"
LOGFILE="/var/log/internet-monitor-agent.log"

. /lib/lsb/init-functions

case "$1" in
  start)
    log_daemon_msg "Starting Internet Monitor Agent"
    start-stop-daemon --start --background --pidfile $PIDFILE \
        --make-pidfile --exec $DAEMON >> $LOGFILE 2>&1
    log_end_msg $?
    ;;
  stop)
    log_daemon_msg "Stopping Internet Monitor Agent"
    start-stop-daemon --stop --pidfile $PIDFILE
    log_end_msg $?
    rm -f $PIDFILE
    ;;
  restart)
    $0 stop
    $0 start
    ;;
  status)
    status_of_proc -p $PIDFILE "$DAEMON" "Internet Monitor Agent"
    ;;
  *)
    echo "Usage: /etc/init.d/internet-monitor-agent {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0
```

Затем сделайте исполняемым и добавьте в автозагрузку:
```bash
sudo chmod +x /etc/init.d/internet-monitor-agent
sudo update-rc.d internet-monitor-agent defaults
```

Такой подход гарантирует:
1. Автоматический запуск при загрузке системы
2. Устойчивость к сбоям (автоматический перезапуск)
3. Централизованное управление через systemd
4. Безопасное хранение учетных данных
5. Логирование в системный журнал
6. Корректную работу с сетевыми интерфейсами
