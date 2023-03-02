Polarion Importer XMLs
######################

Output test case and test run Polarion Importer XMLs ready to import to Polarion
tool.

Enable output
=============

To enable this output, set ``--output-polarion-testcase=$path`` and/or
``--output-polarion-testrun=$path`` together with ``--polarion-config=$path``
command line options.

.. code-block:: bash
    :caption: Example usage

    pytest --collect-only --output-polarion-testcase=./testcase.xml --polarion-config=./polarion.yaml
    pytest --output-polarion-testcase=./testcase.xml --output-polarion-testrun=./testrun.xml --polarion-config=./polarion.yaml

Options
=======

* ``--polarion-config``: Path to the Polarion configuration file
* ``--output-polarion-testcase``: Path to the output Polarion testcase file
* ``--output-polarion-testrun``: Path to the output Polarion testrun file
* ``--polarion-project``: Polarion project ID
* ``--polarion-user``: Polarion user
* ``--polarion-tests-url``: Tests URL
* ``--polarion-create-defects``: Make the importer create defects for failed tests (default ``False``)
* ``--polarion-dry-run``: Indicate to the importer to not make any change (default ``False``)
* ``--polarion-include-skipped``: The importer will include skipped tests (default ``True``)
* ``--polarion-lookup-method``: Indicate to the importer which lookup method to use. ``id`` for work item id or ``custom`` for custom id (default)
* ``--polarion-lookup-method-field-id``: Indicates to the importer which field ID to use when using the 'custom' id lookup method (default ``testCaseID``)
* ``--polarion-testrun-id``: Polarion test run ID
* ``--polarion-testrun-group-id``: Polarion test run group ID
* ``--polarion-testrun-template-id``: Polarion test run template ID
* ``--polarion-testrun-title``: Polarion test run title
* ``--polarion-testrun-type-id``: Polarion test run type ID
* ``--polarion-project-span-ids``: A comma-separated list of project IDs used to set the project span field on the test run
* ``--polarion-testrun-property``: Custom testrun property in key=value format
* ``--polarion-testrun-property-json``: Custom testrun property in JSON format ``{"key": "value", ...}``

Configuration file
==================

.. code-block:: yaml

    project: polarion project name, optional
    user: polarion user name, optional
    tests_url: url to test location, optional
    testcase:
      properties: mapping of polarion properties, optional
      required: mapping of test case required fields
      optional: mapping of test case optional fields
    testrun:
      properties: mapping of polarion properties, optional

.. note::

    Everything but required and optional fields can be also set as command line option.

Fields specification
********************

It is necessary to specify the required and optional test case fields in the
configuration using the following format:

.. code-block:: yaml

    field-name:
      meta: metadata-name, (optional, defaults to field-name)
      multiline: boolean, (optional, default to False for "title", True for other fields)
      validate: value-must-match-this-regex (optional, no validation by default)
      transform: transform value (optional, no transformation by default)
        unless: do-not-transform-if-this-regex-match
        pattern: regex-pattern
        replace: regex-replacement
      default: default value, jinja-template (optional, defaults to no value)
      format: additional html formatting (optional, only "pre" is supported)

For example:

.. code-block:: yaml

    testcase:
      required:
        id:
          default: "tc::{{ item.id }}"
        title:
          transform:
            unless: "Testcase: .*"
            pattern: "^(.*)$"
            replace: "Testcase: \\1"
          validate: "Testcase: (.+)"
        setup:
          format: pre
        steps:
        expectedresults:
        automation_script:
          default: "{{ tests_url }}/{{ item.location.file }}#L{{ item.location.line }}"
      optional:
        teardown:
          format: pre

The value of each field is typically taken from the test docstring metadata that
are set as ``:name: value`` strings. For example:

.. code-block:: python

    def test_example():
        """
        Test description.

        :title: Polarion test title.
        :steps:
          1. Do A
          2. Do B
        :expectedresults:
          1. Expect A
          2. Expect B
        """
        pass

Special fields
--------------

Fields ``steps`` and ``expectedresults`` are special fields. The must follow the
numbered list format that can be seen in the previous example and the numbers in
``steps`` must match the numbers in ``expectedresults``.

Properties specification
************************

The ``properties`` keyword holds mapping of Polarion properties in the following format:

.. code-block:: yaml

    property-name: value

For example:

.. code-block:: yaml

    testcase:
      properties:
        lookup-method: custom
        polarion-custom-lookup-method-field-id: testCaseID
