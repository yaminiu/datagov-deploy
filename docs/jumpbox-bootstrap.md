# Jumpbox bootstrap

This document describes how to configure a newly provisioned jumpbox so that it
can run our Ansible playbooks. This is only needed when provisioning a new
jumpbox.


## Root ssh key

The initial provisioning requires SSH access to the jumpbox. Since the jumpbox playbooks have
not been run, you must use the [environment's root SSH key](https://drive.google.com/drive/folders/10-hk-IqA0jQAW6727pKmW46EF-nHiNLr). Please see a PMO team
member for access.

Add the SSH key to your SSH agent.

    ssh-add ~/.ssh/datagov-sandbox

You must setup ssh-agent forwarding. Add this snippet to your SSH config.

```
# ~/.ssh/config

Host *.datagov.us
    ForwardAgent yes
```


### Bootstraping the jumpbox

When the jumpbox is first created, you'll need to bootstrap it to run ansible.
You can copy/paste these scripts into your terminal. All commands should be run
from the jumpbox.

First, install pyenv.

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
source ~/.bashrc
```

Setup SSH.

```bash
cat <<EOF > ~/.ssh/config
StrictHostKeyChecking=no

Host *.datagov.us
    User ubuntu
    IdentityFile ~/.ssh/authorized_keys
EOF
```

Then setup datagov-deploy.

```bash
git clone https://github.com/GSA/datagov-deploy.git
cd datagov-deploy
pip3 install --user pipenv
pipenv sync
pipenv run make update-vendor-force
```

Symlink the inventory to avoid having to specify it with ansible. _Note: You'll have to
replace the placeholder `<inventory>` with the name of your inventory._

```bash
inventory=<inventory>
sudo mkdir /etc/ansible
sudo ln -s /home/ubuntu/datagov-deploy/ansible/inventories/${inventory} /etc/ansible/hosts
```
