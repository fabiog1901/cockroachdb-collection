
.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. role:: ansible-attribute-support-label
.. role:: ansible-attribute-support-property
.. role:: ansible-attribute-support-full
.. role:: ansible-attribute-support-partial
.. role:: ansible-attribute-support-none
.. role:: ansible-attribute-support-na
.. role:: ansible-option-type
.. role:: ansible-option-elements
.. role:: ansible-option-required
.. role:: ansible-option-versionadded
.. role:: ansible-option-aliases
.. role:: ansible-option-choices
.. role:: ansible-option-choices-default-mark
.. role:: ansible-option-default-bold
.. role:: ansible-option-configuration
.. role:: ansible-option-returned-bold
.. role:: ansible-option-sample-bold

.. Anchors

.. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module:

.. Anchors: short name for ansible.builtin

.. Anchors: aliases



.. Title

fabiog1901.cockroachdb.cc_regions_info module -- List the regions available for new clusters and nodes.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `fabiog1901.cockroachdb collection <https://galaxy.ansible.com/fabiog1901/cockroachdb>`_ (version 1.0.0).

    To install it, use: :code:`ansible-galaxy collection install fabiog1901.cockroachdb`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module_requirements>` for details.

    To use it in a playbook, specify: :code:`fabiog1901.cockroachdb.cc_regions_info`.

.. version_added

.. rst-class:: ansible-version-added

New in fabiog1901.cockroachdb 1.0.0

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- List the regions available for new clusters and nodes.
- A Cockroach Cloud Service Account API Key is required.
- Export the key as environment variable 'CC\_KEY' or pass it on module invokation


.. Aliases


.. Requirements

.. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module_requirements:

Requirements
------------
The below requirements are needed on the host that executes this module.

- cockroachdb-cloud-client






.. Options

Parameters
----------


.. rst-class:: ansible-option-table

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1

  * - Parameter
    - Comments

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client:

      .. rst-class:: ansible-option-title

      **api_client**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Define details for the API client


      .. raw:: html

        </div>
    
  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client/api_version"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client/api_version:

      .. rst-class:: ansible-option-title

      **api_version**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client/api_version" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      The API version to use


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"latest"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client/cc_key"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client/cc_key:

      .. rst-class:: ansible-option-title

      **cc_key**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client/cc_key" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      The Service Account API key

      This value is log redacted

      By default it reads the env variable 'CC\_KEY'


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client/host"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client/host:

      .. rst-class:: ansible-option-title

      **host**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client/host" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      the hostname of the API server


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"cockroachlabs.cloud"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client/path"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client/path:

      .. rst-class:: ansible-option-title

      **path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client/path" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      the path to the API endpoint


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`""`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client/port"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client/port:

      .. rst-class:: ansible-option-title

      **port**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client/port" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      the port number, as a string, for the API server


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"443"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client/scheme"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client/scheme:

      .. rst-class:: ansible-option-title

      **scheme**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client/scheme" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      http or https


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"http"`
      - :ansible-option-choices-entry-default:`"https"` :ansible-option-choices-default-mark:`← (default)`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-api_client/verify_ssl"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-api_client/verify_ssl:

      .. rst-class:: ansible-option-title

      **verify_ssl**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-api_client/verify_ssl" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      whether the client should verify the server cert


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`false`
      - :ansible-option-choices-entry-default:`true` :ansible-option-choices-default-mark:`← (default)`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-provider"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-provider:

      .. rst-class:: ansible-option-title

      **provider**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-provider" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Optional CloudProvider for filtering.

      Must be written in sentences.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"AWS"`
      - :ansible-option-choices-entry:`"GCP"`
      - :ansible-option-choices-entry-default:`"ALL"` :ansible-option-choices-default-mark:`← (default)`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-serverless"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__parameter-serverless:

      .. rst-class:: ansible-option-title

      **serverless**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-serverless" title="Permalink to this option"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Optional filter to only show regions available for serverless clusters.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    
    - name: list CC regions in GCP excluding serverless
      fabiog1901.cockroachdb.cc_regions_info:
      provider: GCP
      serverless: no
      api_client:
        api_version: '2022-09-20'
      register: out




.. Facts


.. Return values

Return Values
-------------
Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this module:

.. rst-class:: ansible-option-table

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1

  * - Key
    - Description

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-regions"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__return-regions:

      .. rst-class:: ansible-option-title

      **regions**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-regions" title="Permalink to this return value"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`list` / :ansible-option-elements:`elements=dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      A list of regions


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`[{"distance": 202.76012, "location": "N. Virginia", "name": "us-east4", "provider": "GCP", "serverless": false}]`


      .. raw:: html

        </div>

    
  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-regions/distance"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__return-regions/distance:

      .. rst-class:: ansible-option-title

      **distance**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-regions/distance" title="Permalink to this return value"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Distance in miles, based on client IP address


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-regions/location"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__return-regions/location:

      .. rst-class:: ansible-option-title

      **location**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-regions/location" title="Permalink to this return value"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      region name


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-regions/name"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__return-regions/name:

      .. rst-class:: ansible-option-title

      **name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-regions/name" title="Permalink to this return value"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      cloud provider location name


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-regions/provider"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__return-regions/provider:

      .. rst-class:: ansible-option-title

      **provider**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-regions/provider" title="Permalink to this return value"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      AWS | GCP


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-regions/serverless"></div>

      .. _ansible_collections.fabiog1901.cockroachdb.cc_regions_info_module__return-regions/serverless:

      .. rst-class:: ansible-option-title

      **serverless**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-regions/serverless" title="Permalink to this return value"></a>

      .. rst-class:: ansible-option-type-line

      :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      region available for serverless clusters


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>




..  Status (Presently only deprecated)


.. Authors

Authors
~~~~~~~

- Cockroach Labs



.. Extra links

Collection links
~~~~~~~~~~~~~~~~

.. raw:: html

  <p class="ansible-links">
    <a href="http://example.com/issue/tracker" aria-role="button" target="_blank" rel="noopener external">Issue Tracker</a>
    <a href="http://example.com" aria-role="button" target="_blank" rel="noopener external">Homepage</a>
    <a href="https://github.com/fabiog1901/cockroachdb-ansible-collection" aria-role="button" target="_blank" rel="noopener external">Repository (Sources)</a>
  </p>

.. Parsing errors

