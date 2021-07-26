# Cloud Instance

Ansible roles for automating the deployment of VMs on the cloud.

You define a list variable `infra` where each item is the definition of a _cluster_, where a cluster can be made up of just 1 VM instance. You can also specify the count of how many such clusters you want to create.

## TO-DO

- Doesn't work for AZURE, only GCP and AWS.

## Requirements

- Ansible v2.9
- openstacksdk
- boto, boto3, botocore

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
      - cloud: openstack # aws, azure, gcp, openstack
        count: 5
        cluster_name: SRM

        region: "{{ region }}" #RegionOne
        vpc_id: "{{ vpc_id }}" # az for openstack, VNet for azure #SE-GOES
        subnet: "{{ subnet }}"
        security_group: "{{ security_group }}" #default
        public_key_id: "{{ public_key }}"

        # image can be a specific cloud provider image name, or use a default
        image: default_centos7
        public_ip: yes
        # if using a default image, no need to specify user
        #  user: centos

        bootstrap:
          openstack: |
            #!/bin/bash
            hostnamectl set-hostname $(echo "`hostname | cut -d"." -f1`.{{ domain|default('') }}")
          aws: ""

        tags:
          owner: "{{ owner }}"
          enddate: "{{ enddate }}"
          project: "{{ project_name }}"
          deployment_id: "{{ deployment_id }}"
          deploy_tool: Foundry

        instance_groups:
          - inventory_groups:
              - main_master
              - db_server
              - cm_server
              - krb5_server
              - cdp_servers
            extra_vars:
              key_str: Hello you!
              key_int: 123
              key_bool: no
            exact_count: 1
            # enter a specific type if desired..
            # instance_type: m5.large
            # .. or use a default one for every cloud provider
            instance:
              gpu: 0
              cpu: 2
              mem: 8
            # volume types are [standard|premium]_[ssd|hdd]
            # defaults to standard_ssd
            volumes:
              - name: /dev/sda1
                type: standard_ssd
                size: 20
                delete_on_termination: true
            tags:
              Name: m

          - inventory_groups:
              - cdf
              - cdp_servers
              - workers
            extra_vars: {}
            exact_count: 2
            instance:
              cpu: 2
              mem: high_mem
            volumes:
              - name: /dev/sda1
                size: 20
                delete_on_termination: true
            tags:
              Name: w


      - cloud: aws
        # count: # default to 1
        # cluster_name: # defaults to 'cluster'

        region: "{{ region }}" #RegionOne
        vpc_id: "{{ vpc_id }}" #SE-GOES
        subnet: "{{ subnet }}"
        security_group: "{{ security_group }}" #default
        public_key_id: "{{ public_key }}"

        image: default_centos7
        public_ip: yes
        bootstrap:
          openstack: |
            #!/bin/bash
            hostnamectl set-hostname $(echo "`hostname | cut -d"." -f1`.{{ domain }}")
        tags:
          owner: "{{ owner }}"
          enddate: "{{ enddate }}"
          project: "{{ project_name }}"
          deployment_id: "{{ deployment_id }}"
          deploy_tool: Foundry

        instance_groups:
          - inventory_groups:
              - freeipa
            extra_vars: {}
            exact_count: 1
            instance:
              cpu: 4
            volumes:
              - name: /dev/sda1
                type: standard_ssd
                size: 100
                delete_on_termination: true
            tags:
              Name: freeipa
  
      - cloud: aws

        region: us-east-1
        vpc_id: vpc-0912105d299a627bf
        subnet: subnet-0fc93769293dc88b8
        security_group: sg-0fe755db5fc1b6120
        public_key_id: public_key  

        image: ami-02eac2c0129f6376b # CentOS-7 x86_64
        user: centos
        public_ip: yes

        bootstrap:
          aws: ""
        tags:
          owner: "{{ owner }}"
          enddate: "{{ enddate }}"
          project: "{{ project_name }}"
          deployment_id: "{{ deployment_id }}"
          deploy_tool: Foundry

        instance_groups:
          - inventory_groups:
              - webserver
            extra_vars: {}
            exact_count: 1
            instance_type: t2.micro
            volumes:
              - name: /dev/sda1
                type: standard_ssd
                size: 20
                delete_on_termination: true
            tags:
              Name: webserver


  tasks:
    - name: ensure presence of instances and Ansible inventory
      include_role:
        name: cloud_instance

- name: FIND RELATIVE CLUSTER MASTER HOST
  hosts: worker
  gather_facts: yes
  tasks:
    - debug:
        msg: "{{ hostvars[(groups[cluster_name] | intersect(groups['main_master']))[0]].public_hostname }}"
```
