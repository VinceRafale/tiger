<VirtualHost 127.0.0.1:8070>
    ServerName reseller.takeouttiger.com
    <Directory /home/threadsafe/tiger/tiger/media/>
        Order deny,allow
        Allow from all
    </Directory>

    LogLevel warn
    ErrorLog  /home/threadsafe/log/apache_error.log
    CustomLog /home/threadsafe/log/apache_access.log combined

    WSGIDaemonProcess reseller.takeouttiger.com user=www-data group=www-data threads=2
    WSGIProcessGroup reseller.takeouttiger.com
    WSGIScriptAlias / /home/threadsafe/tiger/bin/reseller.wsgi
</VirtualHost>
