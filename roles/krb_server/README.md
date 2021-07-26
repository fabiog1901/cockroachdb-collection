# KRB5 Server

Ansible roles for automating the installation of MIT KDC Server packages.

## Requirements

- Ansible v2.8.5

## Role Variables

See example below.

## Dependencies

## Example Playbook

```yml
---
- name: INSTALL MIT KDC SERVER
  hosts: cdpdc
  become: yes
  vars:
    krb5_realm: MYREALM.LOCAL
    krb5_kdc_type: MIT KDC
    krb5_kdc_host: "my-kerberos-server.com"
    krb5_kdc_admin_user: "admin/admin@{{ krb5_realm }}"
    krb5_kdc_admin_passwd: mypassword
    krb5_kdc_master_passwd: mypassword!
    krb5_enc_types: aes256-cts
  
  tasks:

    - name: install MIT KDC server
      include_role:
        name: install_krbserver

```
