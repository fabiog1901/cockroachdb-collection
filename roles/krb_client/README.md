# KRB5 Client

Ansible roles for automating the installation of MIT KDC Client packages.

## Requirements

## Role Variables

## Dependencies

## Example Playbook

```yml
---
- name: INSTALL MIT KDC CLIENT
  hosts: krbclients
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
    - name: install MIT KDC client
      include_role:
        name: install_krbclient
```
