# CockroachDB

This Ansible Role helps you install, configure, start and upgrade a CockroachDB cluster.

## Requirements

- Ansible v2.10

## Role Variables

```yml
cockroachdb_deployment_type: standard
cockroachdb_secure: yes
cockroachdb_krb: no
cockroachdb_certificates_dir: certs
cockroachdb_version: v20.2.4
cockroachdb_join: 
  - "{{ hostvars[( groups[cluster_name] | intersect(groups['cockroachdb']) )[0]].private_hostname }}"
  - "{{ hostvars[( groups[cluster_name] | intersect(groups['cockroachdb']) )[1]].private_hostname }}"
  - "{{ hostvars[( groups[cluster_name] | intersect(groups['cockroachdb']) )[2]].private_hostname }}"
cockroachdb_port: 26257
cockroachdb_http_addr_ip: "0.0.0.0"
cockroachdb_http_addr_port: "8080"

# the value for below vars are fetched individually for each node from hostvars
# these are variables that must be already available in the Ansible inventory
cockroachdb_locality: "region={{ region | default('') }},zone={{ zone | default('') }}"
cockroachdb_advertise_addr: "{{ private_hostname | default('') }}"
cockroachdb_listen_addr: "{{ private_hostname | default('') }}"
cockroachdb_attrs: "{{ extra_vars.attrs | default('std') }}"
cockroachdb_cluster_organization: Workshop
cockroachdb_enterprise_license: crl-0-xxxxyyyyzzzz
```

ansible_facts must be pulled from hosts

```yml
ansible_user: ubuntu

cloud: aws
region: us-east1
zone: b

private_hostname: ip-10-0-5-222.ec2.internal
private_ip: 10.0.5.222
public_hostname: ec2-18-206-87-123.compute-1.amazonaws.com
advertise_addr: 18.206.87.123
```

## Dependencies

None

## Example Playbook

Assuming an Ansible `inventory` like below for a 3 nodes cluster across 3 different AZs in a single Region `us-east-1`

```yml
all:
  vars:
    ansible_user: ubuntu
  hosts:
    18.206.87.123:
      private_hostname: ip-10-0-5-222.ec2.internal
      private_ip: 10.0.5.222
      public_hostname: ec2-18-206-87-123.compute-1.amazonaws.com
      advertise_addr: 18.206.87.123
      cloud: aws
      region: us-east1
      zone: a

    3.221.163.147:
      private_hostname: ip-10-0-5-230.ec2.internal
      private_ip: 10.0.5.230
      public_hostname: ec2-3-221-163-147.compute-1.amazonaws.com
      advertise_addr: 3.221.163.147
      cloud: aws
      region: us-east1
      zone: b

    3.234.141.100:
      private_hostname: ip-10-0-5-52.ec2.internal
      private_ip: 10.0.5.52
      public_hostname: ec2-3-234-141-100.compute-1.amazonaws.com
      advertise_addr: 3.234.141.100
      cloud: aws
      region: us-east1
      zone: c

  children:
    local:
      hosts:
        localhost:
          ansible_connection: local
        
    cockroachdb:
      hosts:
        18.206.87.123:
        3.221.163.147:
        3.234.141.100:
```

Below Play will install and start CockroachDB on the cluster.

```yml
---
- name: DEPLOY COCKROACHDB
  hosts: cockroachdb
  gather_facts: yes
  become: yes
  tasks:
    - include_role:
        name: cockroachdb
      vars:
        cockroachdb_deployment_type: standard
        cockroachdb_version: latest
        cockroachdb_secure: no
        cockroachdb_port: 26257
        cockroachdb_http_addr_ip: '0.0.0.0'
        cockroachdb_http_addr_port: 8080
        cockroachdb_join: 
          - host1
          - host2
          - host3
        cockroachdb_locality: "region={{ region }},zone={{ zone }}"
        cockroachdb_advertise_addr: "{{ private_hostname }}"
        cockroachdb_listen_addr: "{{ private_hostname }}"
```
