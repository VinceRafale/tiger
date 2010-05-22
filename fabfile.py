import os
from fabric.api import *

prod = 'threadsafe@takeouttiger.com:1123'
staging = 'threadsafe@demo.takeouttiger.com:1123'

def deploy():
    with cd('/home/threadsafe/tiger/'):
        sudo('chown -R threadsafe:threadsafe tiger/media')
        run('git pull origin master')
        run('bin/buildout -N -c production.cfg')
        run('bin/django syncdb')
        run('bin/django migrate')
        sudo('chown -R www-data:www-data tiger/media')
        run('touch bin/django.wsgi')

@hosts(staging)
def deploy_staging():
    deploy()

@hosts(prod)
def deploy_prod():
    deploy()

def apply_remote_changes():
    with cd('/home/threadsafe/tiger/'):
        run('git stash')
        run('git pull origin master')
        run('git stash apply')
        run('git diff > temp.diff')
        run('git checkout .')
    get('/home/threadsafe/tiger/temp.diff', '.')
    local('git apply temp.diff')
