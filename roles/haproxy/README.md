# HAProxy

This Ansible Role helps you install, configure and start a HAProxy cluster.

## Requirements

- Ansible v2.10

## Role Variables

```yml
haproxy_group: list of hosts in hostvars
haproxy_port: bind port
haproxy_checkport: checkport
haproxy_serverprefix: server name
haproxy_httpchk: path to httpcheck
```

## Dependencies

None

## Example Playbook

Below Play will install and start HAProxy.

```yml
---
- name: INSTALL HAPROXY
  hosts: haproxy
  gather_facts: yes
  become: yes
  tasks:
    - name: install HAProxy
      include_role:
        name: haproxy
      vars:
        haproxy_group: "{{ groups['webservers'] }}"
        haproxy_port: '26257'
        haproxy_checkport: '8080'
        haproxy_serverprefix: cockroach
        haproxy_httpchk: '/health?ready=1'
  tags:
    - haproxy
```
