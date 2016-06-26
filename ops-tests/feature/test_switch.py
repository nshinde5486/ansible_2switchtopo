# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import time


TOPOLOGY = """
#
#      +-----------------+             +------------+
#      |     Ansible     | eth0   eth0 |            |
#      | control machine |-------------| OpenSwitch |
#      |    (server)     |             |  (switch)  |
#      +-----------------+             +------------+
#
# Nodes
[type=oobmhost name="server"] server
[type=openswitch name="switch"] switch
#
# Links
[force_name=oobm] switch:eth0
server:eth0 -- switch:eth0
"""


def _setup(topo):
    """ setup server and switch to be ready for the ansible play """
    server = topo.get('server')
    switch = topo.get('switch')

    # Wait switch to come up
    time.sleep(10)

    # Server IP address
    server.libs.ip.interface('eth0', addr='192.168.1.254/24', up=True)

    # Switch IP address
    with switch.libs.vtysh.ConfigInterfaceMgmt() as ctx:
        ctx.ip_static('192.168.1.1/24')

    # Copy SSH public key through playbook
    _test_playbook(server, 'utils/copy_public_key.yaml', ops='-u root')

    return server


def _cmd(playbook, ops=''):
    return "ansible-playbook %s /etc/ansible/%s" % (ops, playbook)


def _test_playbook(server, playbook, ops=''):
    server(_cmd(playbook, ops))
    assert '0' == server('echo $?'), "fail in %s" % playbook


def test_hostname(topology, step):
    playbook = 'roles/switch/tests/test_hostname.yml'
    server = _setup(topology)
    step("Test %s playbook" % playbook)
    _test_playbook(server, playbook, ops='-v')
