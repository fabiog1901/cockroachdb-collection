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
        certificates:
          organization_name: cockroachlabs
          dir: my-certs
          usernames:
            - root
          hosts: "{{ groups['my-inventory-group'] }}"
```
