#!/bin/bash

ready_workspace(){
    if [ ! -f "/home/init.locked" ]; then
        rm -rf /etc/ssh
        mkdir -p /data/ssh
        ln -s /data/ssh /etc/ssh

        rm -rf /home
        mkdir -p /data/home
        ln -s /data/home /home

        mkdir -p /data/logs
        ln -s /data/logs ./logs
        chmod -R 777 /data/logs

        mkdir -p /data/keys
        ln -s /data/keys ./keys
        chmod -R 777 /data/keys

        rm -rf /etc/ansible
        mkdir -p /data/ansible
        ln -s /data/ansible /etc/ansible
        cp ./install/docker/ansible.cfg /data/ansible/ansible.cfg

        date > /home/init.locked
    fi
}

init_db(){
    if [ ! -f "/home/init_db.locked" ]; then
        python3 manage.py loaddata install/initial_data.yaml
        date > /home/init_db.locked
    else
        echo 'database had been inited, skip.'
    fi
}

ready_jmps_config(){
    cp -r ./install/docker/config_tmpl.conf ./jumpserver.conf

    # server url
    if [ ! -n "${SERVER_URL}" ]; then
        sed -i "s/__SERVER_URL__//" ./jumpserver.conf
    else
        sed -i "s/__SERVER_URL__/${SERVER_URL}/" ./jumpserver.conf
    fi

    # crypt key
    if [ ! -n "${CRYPT_KEY}" ]; then
        sed -i "s/__CRYPT_KEY__/941enj9neshd1wes/" ./jumpserver.conf
    else
        sed -i "s/__CRYPT_KEY__/${CRYPT_KEY}/" ./jumpserver.conf
    fi

    # db
    if [ ! -n "${USE_MYSQL}" ]; then
        sed -i "s/__USE_MYSQL__/false/" ./jumpserver.conf
    else
        sed -i "s/__MYSQL_ENGINE__/${MYSQL_ENGINE}/" ./jumpserver.conf
        sed -i "s/__MYSQL_HOST__/${MYSQL_HOST}/" ./jumpserver.conf
        sed -i "s/__MYSQL_PORT__/${MYSQL_PORT}/" ./jumpserver.conf
        sed -i "s/__MYSQL_USER__/${MYSQL_USER}/" ./jumpserver.conf
        sed -i "s/__MYSQL_PASS__/${MYSQL_PASS}/" ./jumpserver.conf
        sed -i "s/__MYSQL_NAME__/${MYSQL_NAME}/" ./jumpserver.conf
    fi

    # email
    if [ ! -n "${USE_MAIL}" ]; then
        sed -i "s/__USE_MAIL__/false/" ./jumpserver.conf
    else
        sed -i "s/__MAIL_ENABLED__/${MAIL_ENABLED}/" ./jumpserver.conf
        sed -i "s/__MAIL_HOST__/${MAIL_HOST}/" ./jumpserver.conf
        sed -i "s/__MAIL_PORT__/${MAIL_PORT}/" ./jumpserver.conf
        sed -i "s/__MAIL_USER__/${MAIL_USER}/" ./jumpserver.conf
        sed -i "s/__MAIL_PASS__/${MAIL_PASS}/" ./jumpserver.conf
    fi

    if [ ! -n "${MAIL_USE_TLS}" ]; then
        sed -i "s/__MAIL_USE_TLS__/false/" ./jumpserver.conf
    else
        sed -i "s/__MAIL_USE_TLS__/${MAIL_USE_TLS}/" ./jumpserver.conf
    fi

    if [ ! -n "${MAIL_USE_SSL}" ]; then
        sed -i "s/__MAIL_USE_SSL__/false/" ./jumpserver.conf
    else
        sed -i "s/__MAIL_USE_SSL__/${MAIL_USE_SSL}/" ./jumpserver.conf
    fi

    # brand
    if [ ! -n "${BRAND}" ]; then
        sed -i "s/__BRAND__/Jumpserver/" ./jumpserver.conf
    else
        sed -i "s/__BRAND__/${BRAND}/" ./jumpserver.conf
    fi

    if [ ! -n "${LOGO_128}" ]; then
        sed -i "s#__LOGO_128__#img/logo.png#" ./jumpserver.conf
    else
        sed -i "s#__LOGO_128__#${LOGO_128}#" ./jumpserver.conf
    fi

    if [ ! -n "${COPYRIGHT}" ]; then
        sed -i "s/__COPYRIGHT__/Jumpserver.org Organization © 2014-2015/" ./jumpserver.conf
    else
        sed -i "s/__COPYRIGHT__/${COPYRIGHT}/" ./jumpserver.conf
    fi

    # guacamole (win server audit)
    if [ ! -n "${GUACAMOLE_WEB_SERVER}" ]; then
        sed -i "s/__GUACAMOLE_WEB_SERVER__//" ./jumpserver.conf
    else
        sed -i "s/__GUACAMOLE_WEB_SERVER__/${GUACAMOLE_WEB_SERVER}/" ./jumpserver.conf
    fi
}

ready_ssh(){
    if [ ! -f "/etc/ssh/sshd_config" ]; then
        cp -r ./install/docker/sshd_config /etc/ssh/sshd_config
    fi

    if [ ! -f "/etc/ssh/ssh_host_rsa_key" ]; then
      ssh-keygen -t rsa -b 2048 -f /etc/ssh/ssh_host_rsa_key -N ''
    fi

    if [ ! -f "/etc/ssh/ssh_host_dsa_key" ]; then
      ssh-keygen -t dsa -b 1024 -f /etc/ssh/ssh_host_dsa_key -N ''
    fi

    if [ ! -f "/etc/ssh/ssh_host_ecdsa_key" ]; then
      ssh-keygen -t ecdsa -b 521 -f /etc/ssh/ssh_host_ecdsa_key -N ''
    fi

    if [ ! -f "/etc/ssh/ssh_host_ed25519_key" ]; then
      ssh-keygen -t ed25519 -b 1024 -f /etc/ssh/ssh_host_ed25519_key -N ''
    fi
}

migrate_db(){
    # migrate
    python3 manage.py makemigrations && python3 manage.py migrate
}

cronjob(){
    python3 manage.py crontab add
}

work(){
    ready_workspace
    ready_jmps_config
    ready_ssh
    migrate_db
    init_db
    cronjob
}

work

_term() {
    echo "Caught SIGTERM signal, forward to child"
    kill -TERM "$child"
    exit 0
}

trap _term SIGTERM
python3 run_server.py &
child=$!
wait "$child"
