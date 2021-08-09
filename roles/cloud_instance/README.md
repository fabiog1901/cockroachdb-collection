# Cloud Instance

Ansible roles for automating the deployment of VMs on the cloud.

You define a list variable `infra` where each item is the definition of a _cluster_, where a cluster can be made up of just 1 VM instance. You can also specify the count of how many such clusters you want to create.

## Requirements

- Ansible v2.9
- boto, boto3, botocore, google-auth

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
# create:
# - five 3-nodes clusters (1 master, 2 workers) on OpenStack,
# - a single VM for FreeIPA on OpenStack,
# - a single VM for a webserver in AWS.
- name: PROVISION HOSTS AND BUILD ANSIBLE HOSTS INVENTORY
  hosts: localhost
  connection: local
  gather_facts: no
  become: no
  vars:
    infra:
      - cloud: aws
        count: 1 # default to 1
        cluster_name: demo # defaults to 'cluster'
        region: us-east1
        vpc_id: vpc-123
        subnet: subnet-456
        security_group: sg-987
        public_key_id: workshop
        image: default_centos7
        public_ip: yes
        bootstrap:
          aws: |
            #!/bin/bash
            touch hello-aws
        tags:
          owner: fabio
          deployment_id: demo1

        instance_groups:
          - inventory_groups:
              - appservers
            extra_vars: {}
            exact_count: 1
            instance:
              cpu: 4
            volumes:
              - type: standard_ssd
                size: 100
                delete_on_termination: true
            tags:
              Name: freeipa

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
