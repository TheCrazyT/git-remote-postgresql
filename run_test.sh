#!/bin/bash

mkdir -p ~/.local/bin
cp git-remote-postgresql ~/.local/bin
chmod +x ~/.local/bin/git-remote-postgresql
PATH=$PATH:~/.local/bin

git config --global credential.helper store

echo -e "protocol=postgresql\nhost=127.0.0.1\nusername=username\npassword=password"|git credential approve
sudo apt update
sudo apt install -y postgresql python3
pip install pexpect
sudo /etc/init.d/postgresql start

sudo -u postgres -i psql -c "CREATE DATABASE the_db"
sudo -u postgres -i psql -d the_db -c "CREATE TABLE test (x INTEGER)"
sudo -u postgres -i psql -d the_db -c "CREATE USER username WITH PASSWORD 'password'"
sudo -u postgres -i psql -d the_db -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO username"
sudo -u postgres -i psql -d the_db -c "GRANT ALL ON SCHEMA public TO username"

GR_PSQL_DEBUG=1 git clone postgresql://127.0.0.1:5432/the_db
