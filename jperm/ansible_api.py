#!/usr/bin/env python3
# coding=utf-8
import json
from tempfile import NamedTemporaryFile
from passlib.hash import sha512_crypt

from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback.json import CallbackModule
from ansible.vars import VariableManager
from django.template.loader import get_template
from django.template import Context


class MyInventory(Inventory):

    def __init__(self, resource, loader, variable_manager, host_list=[]):
        '''
        resource的数据格式是一个列表字典，比如
            {
                "group1": {
                    "hosts": [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...],
                    "vars": {"var1": value1, "var2": value2, ...}
                }
            }

        如果你只传入1个列表，这默认该列表内的所有主机属于my_group组,比如
            [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...]
        '''
        super(MyInventory, self).__init__(loader=loader, variable_manager=variable_manager, host_list=host_list)
        self.resource = resource
        self.gen_inventory()

    def my_add_group(self, hosts, groupname, groupvars=None):
        '''
        add hosts to a group
        '''
        my_group = Group(name=groupname)

        # if group variables exists, add them to group
        if groupvars:
            for key, value in groupvars.items():
                my_group.set_variable(key, value)

        # add hosts to group
        for host in hosts:
            # set connection variables
            hostname = host.get('hostname')
            hostip = host.get('ip', hostname)
            hostport = host.get('port')
            username = host.get('username')
            password = host.get('password')
            ssh_key = host.get('ssh_key')
            my_host = Host(name=hostname, port=hostport)
            my_host.set_variable('ansible_ssh_host', hostip)
            my_host.set_variable('ansible_ssh_port', hostport)
            my_host.set_variable('ansible_ssh_user', username)
            my_host.set_variable('ansible_ssh_pass', password)
            my_host.set_variable('ansible_ssh_private_key_file', ssh_key)

            # set other variables
            for key, value in host.items():
                if key not in ['hostname', 'port', 'username', 'password']:
                    my_host.set_variable(key, value)
            # add to group
            my_group.add_host(my_host)

        self.add_group(my_group)

    def gen_inventory(self):
        '''
        add hosts to inventory.
        '''
        if isinstance(self.resource, list):
            self.my_add_group(self.resource, 'default_group')

        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.iteritems():
                self.my_add_group(hosts_and_vars.get('hosts'), groupname, hosts_and_vars.get('vars'))


class Options(object):
    '''
    Options class to replace Ansible OptParser
    '''
    def __init__(self, verbosity=None, inventory=None, listhosts=None, subset=None, module_paths=None, extra_vars=None,
                 forks=None, ask_vault_pass=None, vault_password_files=None, new_vault_password_file=None,
                 output_file=None, tags=None, skip_tags=None, one_line=None, tree=None, ask_sudo_pass=None, ask_su_pass=None,
                 sudo=None, sudo_user=None, become=None, become_method=None, become_user=None, become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None, connection=None, timeout=None, ssh_common_args=None,
                 sftp_extra_args=None, scp_extra_args=None, ssh_extra_args=None, poll_interval=None, seconds=None, check=None,
                 syntax=None, diff=None, force_handlers=None, flush_cache=None, listtasks=None, listtags=None, module_path=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = tags
        self.skip_tags = skip_tags
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path


class MyRunner:

    def __init__(self, resource):
        self.options = Options()
        self.options.connection = 'ssh'  # Need a connection type 'smart' or 'ssh'
        self.options.become = True
        self.options.become_method = 'sudo'
        self.options.become_user = 'root'

        # Become Pass Needed if not logging in as user root (do not support now)
        passwords = {'become_pass': ''}

        # Gets data from YAML/JSON files
        self.loader = DataLoader()

        # All the variables from all the various places
        self.variable_manager = VariableManager()

        # Set inventory, using most of above objects
        self.inventory = MyInventory(resource=resource, loader=self.loader, variable_manager=self.variable_manager)
        self.variable_manager.set_inventory(self.inventory)

        # set callback object
        self.results_callback = CallbackModule()

        # playbook
        self.tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=passwords,
            stdout_callback=self.results_callback,
        )

    def run(self, module_name='shell', module_args='', gather_facts=False, pattern='*'):
        play_source = dict(
            name='Ansible Play',
            hosts=pattern,
            gather_facts=gather_facts,
            tasks=[
                dict(action=dict(module=module_name, args=module_args)),
            ]
        )

        self.play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        self.tqm.run(self.play)
        self.result_raw = self.results_callback.results
        return self.result_raw

    def close(self):
        self.tqm.cleanup()

    @property
    def results(self):
        """
        {'failed': {'localhost': ''}, 'ok': {'jumpserver': ''}}
        """
        result = {'failed': {}, 'ok': {}}

        results = self.result_raw[-1]
        tasks = results.get('tasks', {})
        hosts = tasks[0].get('hosts', {})

        for host, info in hosts.items():
            if info.get('unreachable') or info.get('failed'):
                result['failed'][host] = info.get('msg')
            else:
                if info.get('invocation').get('module_name') in ['raw', 'shell', 'command', 'script']:
                    if info.get('rc') == 0:
                        result['ok'][host] = info.get('stdout') + info.get('stderr')
                    else:
                        result['failed'][host] = info.get('stdout') + info.get('stderr')
                elif info.get('invocation').get('module_name') in ['setup']:
                    result['ok'][host] = info.get('ansible_facts')
                else:
                    if info.get('failed'):
                        result['failed'][host] = info.get('msg')
                    else:
                        result['ok'][host] = info.get('changed')
        return result


class MyTask(MyRunner):
    """
    this is a tasks object for include the common command.
    """
    def __init__(self, *args, **kwargs):
        super(MyTask, self).__init__(*args, **kwargs)

    def push_key(self, user, key_path):
        """
        push the ssh authorized key to target.
        """
        module_args = 'user="%s" key="{{ lookup("file", "%s") }}" state=present' % (user, key_path)
        self.run("authorized_key", module_args, become=True)

        return self.results

    def push_multi_key(self, **user_info):
        """
        push multi key
        :param user_info:
        :return:
        """
        ret_failed = []
        ret_success = []
        for user, key_path in user_info.items():
            ret = self.push_key(user, key_path)
            if ret.get("status") == "ok":
                ret_success.append(ret)
            if ret.get("status") == "failed":
                ret_failed.append(ret)

        if ret_failed:
            return {"status": "failed", "msg": ret_failed}
        else:
            return {"status": "success", "msg": ret_success}

    def del_key(self, user, key_path):
        """
        push the ssh authorized key to target.
        """
        if user == 'root':
            return {"status": "failed", "msg": "root cann't be delete"}
        module_args = 'user="%s" key="{{ lookup("file", "%s") }}" state="absent"' % (user, key_path)
        self.run("authorized_key", module_args, become=True)

        return self.results

    def add_user(self, username, password=''):
        """
        add a host user.
        """

        if password:
            encrypt_pass = sha512_crypt.encrypt(password)
            module_args = 'name=%s shell=/bin/bash password=%s' % (username, encrypt_pass)
        else:
            module_args = 'name=%s shell=/bin/bash' % username

        self.run("user", module_args, become=True)

        return self.results

    def add_multi_user(self, **user_info):
        """
        add multi user
        :param user_info: keyword args
            {username: password}
        :return:
        """
        ret_success = []
        ret_failed = []
        for user, password in user_info.items():
            ret = self.add_user(user, password)
            if ret.get("status") == "ok":
                ret_success.append(ret)
            if ret.get("status") == "failed":
                ret_failed.append(ret)

        if ret_failed:
            return {"status": "failed", "msg": ret_failed}
        else:
            return {"status": "success", "msg": ret_success}

    def del_user(self, username):
        """
        delete a host user.
        """
        if username == 'root':
            return {"status": "failed", "msg": "root cann't be delete"}
        module_args = 'name=%s state=absent remove=yes move_home=yes force=yes' % username
        self.run("user", module_args, become=True)
        return self.results

    def del_user_sudo(self, username):
        """
        delete a role sudo item
        :param username:
        :return:
        """
        if username == 'root':
            return {"status": "failed", "msg": "root cann't be delete"}
        module_args = "sed -i 's/^%s.*//' /etc/sudoers" % username
        self.run("command", module_args, become=True)
        return self.results

    @staticmethod
    def gen_sudo_script(role_list, sudo_list):
        # receive role_list = [role1, role2] sudo_list = [sudo1, sudo2]
        # return sudo_alias={'NETWORK': '/sbin/ifconfig, /ls'} sudo_user={'user1': ['NETWORK', 'SYSTEM']}
        sudo_alias = {}
        sudo_user = {}
        for sudo in sudo_list:
            sudo_alias[sudo.name] = sudo.commands

        for role in role_list:
            sudo_user[role.name] = ','.join(list(sudo_alias.keys()))

        sudo_j2 = get_template('jperm/role_sudo.j2')
        sudo_content = sudo_j2.render(Context({"sudo_alias": sudo_alias, "sudo_user": sudo_user}))
        sudo_file = NamedTemporaryFile(delete=False)
        sudo_file.write(sudo_content)
        sudo_file.close()
        return sudo_file.name

    def push_sudo_file(self, role_list, sudo_list):
        """
        use template to render pushed sudoers file
        :return:
        """
        module_args1 = self.gen_sudo_script(role_list, sudo_list)
        self.run("script", module_args1, become=True)
        return self.results

    def recyle_cmd_alias(self, role_name):
        """
        recyle sudo cmd alias
        :return:
        """
        if role_name == 'root':
            return {"status": "failed", "msg": "can't recyle root privileges"}
        module_args = "sed -i 's/^%s.*//' /etc/sudoers" % role_name
        self.run("command", module_args, become=True)
        return self.results


if __name__ == '__main__':
    res = [
        {
            'ssh_key': '/home/choldrim/SRC/PYTHON/jumpserver-new/keys/user/admin_deepin.pem',
            'username': 'deepin',
            'ip': '10.10.120.114',
            'hostname': 'payOrder-provider01',
            'port': 16001,
            'password': 'deepin'
        },
        {
            'ssh_key': '/home/choldrim/SRC/PYTHON/jumpserver-new/keys/user/admin_deepin.pem',
            'username': 'deepin',
            'ip': '10.10.120.114',
            'hostname': 'payOrder-provider02',
            'port': 16002,
            'password': 'deepin'
        }
    ]
    tqm = MyRunner(res)
    #result = tqm.run(module_name='shell', module_args='ls /')
    result = tqm.run(module_name='copy', module_args='src=/tmp/files.zip dest=/tmp')
    print(json.dumps(result, indent=4))
    #print(json.dumps(tqm.results, indent=4))
