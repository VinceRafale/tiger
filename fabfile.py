import os
from fabric.api import *
from fabric.contrib.files import append

prod = 'threadsafe@takeouttiger.com:1123'
staging = 'threadsafe@demo.takeouttiger.com:1123'

def deploy(branch):
    local('git push origin %s' % branch)
    with cd('/home/threadsafe/tiger/'):
        run('git pull origin %s' % branch)
        run('bin/buildout -N -c production.cfg')
        run('bin/django syncdb')
        run('bin/django migrate')
        run('touch bin/django.wsgi')
        run('touch bin/tiger.wsgi')
        run('touch bin/reseller.wsgi')
        sudo('/etc/init.d/celeryd stop')
        sudo('/etc/init.d/celeryd start')

@hosts(staging)
def deploy_staging():
    deploy('staging')

@hosts(prod)
def deploy_prod():
    deploy('master')

def apply_remote_changes():
    with cd('/home/threadsafe/tiger/'):
        run('git stash')
        run('git pull origin master')
        run('git stash apply')
        run('git diff > temp.diff')
        run('git checkout .')
    get('/home/threadsafe/tiger/temp.diff', '.')
    local('git apply temp.diff')
