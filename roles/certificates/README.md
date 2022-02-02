# Certificates

Ansible role to create certificates and keys for a set of hosts and users.

<https://www.cockroachlabs.com/docs/stable/create-security-certificates-openssl>

## Requirements

## Role Variables

## Dependencies

## Example Playbook

```yml
- name: generate certs
  hosts: localhost
  gather_facts: no
  become: no
  tasks:
    - include_role:
        name: certificates
      vars:
        certificates_organization_name: cockroachlabs
        certificates_dir: my-certs
        certificates_usernames:
            - root
        certificates_hosts: "{{ groups['my-inventory-group'] }}"
        certificates_loadbalancer: "{{ groups['my-lb-group'] }}"
```
