crontab cron_schedule && crond
waitress-serve --call monitor:create_app