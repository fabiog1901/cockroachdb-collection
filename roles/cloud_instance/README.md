# Cloud Instance

Ansible roles for automating the deployment of VMs on the cloud.

You define a list variable `infra` where each item is the definition of a _cluster_, where a cluster can be made up of just 1 VM instance. You can also specify the count of how many such clusters you want to create.

## Requirements

## Role Variables

Variable `instance_type` can be used to set a specific instance type. As such, it won't work across all cloud providers.

Variable `instance` is a dict with 3 keys:

- `gpu`: defaults to 0.
- `cpu`: defaults to 16.
- `mem`: defaults to 4 times the number of `cpu`. `mem` also takes `high_cpu`, `default` and `high_mem` as values.

Examples:

```yml
# create instance with 8 CPUs and 32 Mem
instance:
  cpu: 8

# create instance with 8 CPUs and 32 Mem
instance:
  cpu: 8
  mem: 32

# create instance with 8 CPUs, optimized for high mem
instance:
  cpu: 8
  mem: high_mem

# create instance with 8 CPUs, optimized for high mem
instance:
  cpu: 8
  mem: 64
```  

Check file `defaults/main.yml` for the list of all pre-configured instances.

## Dependencies

## Example Playbook

```yml
---
- name: PROVISION HOSTS AND BUILD ANSIBLE HOSTS INVENTORY
  hosts: localhost
  connection: local
  gather_facts: no
  become: no
  vars:
    infra:
      - cluster_name: demo
        instance_groups:
          - user: ubuntu
            public_ip: yes
            public_key_id: workshop
            tags:
              owner: "{{ owner }}"
              deployment_id: "{{ deployment_id }}"
            cloud: gcp
            image: projects/ubuntu-os-cloud/global/images/family/ubuntu-2004-lts
            security_group:
              - cockroachdb
            region: us-central1
            vpc_id: default
            zone: a
            subnet: default
            inventory_groups:
              - krb5_server
            exact_count: 1
            instance:
              cpu: 2
              mem: 4
            volumes:
              os:
                size: 10
                type: standard_ssd
              data: []
            tags:
              Name: "{{ deployment_id }}-kdc"

  tasks:
    - name: ensure presence of instances and Ansible inventory
      include_role:
        name: cloud_instance

- name: FIND RELATIVE CLUSTER MASTER HOST
  hosts: appservers
  gather_facts: yes
  tasks:
    - debug:
        msg: "{{ hostvars[(groups[cluster_name] | intersect(groups['master']))[0]].public_hostname }}"
```
