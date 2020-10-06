import os
from datetime import datetime

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


virtualenv_path = '/usr/lib/ckan'
catalog_host_public = 'catalog.localdomain.local'
catalog_host_public_next = 'catalog-next.localdomain.local'


def test_var_lib_ckan(host):
    var_lib_ckan = host.file('/var/lib/ckan')

    assert var_lib_ckan.exists
    assert var_lib_ckan.is_directory
    assert var_lib_ckan.user == 'www-data'
    assert var_lib_ckan.group == 'www-data'
    assert var_lib_ckan.mode == 0o755


def test_var_tmp_ckan(host):
    var_tmp_ckan = host.file('/var/tmp/ckan')

    assert var_tmp_ckan.exists
    assert var_tmp_ckan.is_directory
    assert var_tmp_ckan.user == 'www-data'
    assert var_tmp_ckan.group == 'www-data'
    assert var_tmp_ckan.mode == 0o755


def test_dynamic_menu(host):
    """Test menu.json is prepopulated with old modification time
    https://github.com/GSA/catalog-app/issues/76"""
    dynamic_menu = host.file('/var/tmp/ckan/dynamic_menu/menu.json')

    assert dynamic_menu.exists
    assert dynamic_menu.user == 'www-data'
    assert dynamic_menu.group == 'www-data'
    assert dynamic_menu.mode == 0o644
    # We do a loose assertion on mtime to avoid timezone issues
    assert dynamic_menu.mtime < datetime(2020, 1, 2)


def test_production_ini(host):
    production_ini = host.file('/etc/ckan/production.ini')

    assert production_ini.exists
    assert production_ini.user == 'root'
    assert production_ini.group == 'www-data'
    assert production_ini.mode == 0o640

    assert production_ini.contains('ckan.plugins =.*datajson')
    assert production_ini.contains('ckan.plugins =.*saml2')


def test_who_ini(host):
    who_ini = host.file('/etc/ckan/who.ini')

    assert who_ini.exists
    assert who_ini.user == 'root'
    assert who_ini.group == 'www-data'
    assert who_ini.mode == 0o640

    assert who_ini.contains('saml2auth')


def test_compatible_repoze_who(host):
    packages = host.pip_package.get_packages(
        pip_path=('%s/bin/pip' % virtualenv_path)
    )

    assert 'repoze.who' in packages
    assert 'Paste' in packages

    assert '2.3' == packages['repoze.who'].get('version')
    assert '1.7.5.1' == packages['Paste'].get('version')


def test_apache(host):
    apache = host.service('apache2')

    assert apache.is_running
    assert apache.is_enabled


def test_gunicorn_conf(host):
    f = host.file('/etc/supervisor/conf.d/supervisord_gunicorn.conf')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.mode == 0o644
    assert f.contains('[program:catalog-web]')


def test_apache_site(host):
    f = host.file('/etc/apache2/sites-enabled/ckan.conf')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'www-data'
    assert f.mode == 0o644
    assert f.contains('ErrorLog /var/log/ckan/ckan.error.log')

    # catalog domain ServerName, catalog-next in ServerAlias
    assert f.contains('ServerName %s' % catalog_host_public)
    assert f.contains('ServerAlias %s' % catalog_host_public_next)
