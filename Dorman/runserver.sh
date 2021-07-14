#!/bin/bash
export APP_SETTINGS="config.DevelopmentConfig"
. /root/s3store/bin/activate
cd /root/Dorman/
python app.py
