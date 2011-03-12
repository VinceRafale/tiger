server {
    listen 80;
    server_name _;
    if ($host ~* ^([\w-]+\.takeouttiger.com)$) {
        set $subdomain $1;
        rewrite ^(.*)$ https://$subdomain$1 permanent;
    }
    if ($host ~* ^([\w-]+\.[a-z]+)$) {
        set $host_without_www www.$1;
        rewrite ^(.*)$ http://$host_without_www$1 permanent;
    }

    access_log /home/threadsafe/log/access.log;
    error_log /home/threadsafe/log/error.log;

    location / {
        include       /etc/nginx/proxy.conf;
        proxy_pass    http://127.0.0.1:8080;
    }

    location /static/ {
        alias   /home/threadsafe/tiger/tiger/media/;
    }

    location /media/ {
        alias   /home/threadsafe/tiger/parts/django/django/contrib/admin/media/;
    }

    location /favicon.ico {
        alias   /home/threadsafe/tiger/tiger/media/img/favicon.ico;
    }

}

server {
    listen 443;

    ssl on;
    ssl_certificate    /etc/ssl/takeouttiger.com.crt;
    ssl_certificate_key    /etc/ssl/takeouttiger.com.key;

    server_name *.takeouttiger.com;

    if ($host ~* ^([\w-]+\.[a-z]+)$) {
        set $host_without_www www.$1;
        rewrite ^(.*)$ http://$host_without_www$1 permanent;
    }

    access_log /home/threadsafe/log/access.log;
    error_log /home/threadsafe/log/error.log debug;

    location / {
        include       /etc/nginx/proxy.conf;
        if ($host ~* ^www.takeouttiger.com$) {
            proxy_pass    http://127.0.0.1:8060;
            break;
        }
        if ($host ~* ^reseller.takeouttiger.com$) {
            proxy_pass    http://127.0.0.1:8070;
            break;
        }
        proxy_pass    http://127.0.0.1:8080;
    }

    location /static/ {
        alias   /home/threadsafe/tiger/tiger/media/;
    }

    location /media/ {
        alias   /home/threadsafe/tiger/parts/django/django/contrib/admin/media/;
    }
}
