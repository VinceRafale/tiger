<VirtualHost 127.0.0.1:8060>
    ServerName *
    <Directory /home/threadsafe/tiger/tiger/apache/>
        Order deny,allow
        Allow from all
    </Directory>
    <Directory /home/threadsafe/tiger/tiger/media/>
        Order deny,allow
        Allow from all
    </Directory>

    LogLevel warn
    ErrorLog  /home/threadsafe/log/apache_error.log
    CustomLog /home/threadsafe/log/apache_access.log combined

    WSGIDaemonProcess www.takeouttiger.com user=www-data group=www-data threads=4
    WSGIProcessGroup www.takeouttiger.com
    WSGIScriptAlias / /home/threadsafe/tiger/bin/tiger.wsgi
</VirtualHost>

