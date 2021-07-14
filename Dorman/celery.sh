#!/bin/bash
export APP_SETTINGS="config.DevelopmentConfig"
. /root/s3store/bin/activate
cd /root/Dorman/
celery worker -A app.celery --loglevel=info  -f /root/Dorman/scrapylog.log
