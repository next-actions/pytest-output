from __future__ import annotations

import sys

import pytest


@pytest.fixture
def error_setup():
    raise ValueError("error")


@pytest.fixture
def error_teardown():
    yield
    raise ValueError("error")


@pytest.mark.parametrize("arg", [1, 2])
def test_success(arg):
    """
    My custom string.

    :title: Success
    :setup:
        1. Create local user "user-1"
        2. Add local rule to /etc/sudoers to allow all commands for "user-1"
        3. Enable sudo responder
        4. Set entry_negative_timeout to 0 to disable standard negative cache
        5. Start SSSD
    :steps:
        1. Authenticate as "user-1" over SSH
        2. Run "sudo /bin/ls /root"
        3. Start tcpdump to capture ldap packets and run "sudo /bin/ls /root" multiple times again
    :expectedresults:
        1. User is logged into the host
        2. Command is successful, user is stored in negative cache for local users
        3. No ldap packets for "user-1" user resolution are sent
    :customerscenario: True
    """
    print("test stdout")
    print("test stderr", file=sys.stderr)
    pass


def test_failure_assert():
    """
    My custom string.

    :title: Failure assertion
    :setup:
        1. Create local user "user-1"
        2. Add local rule to /etc/sudoers to allow all commands for "user-1"
        3. Enable sudo responder
        4. Set entry_negative_timeout to 0 to disable standard negative cache
        5. Start SSSD
    :steps:
        1. Authenticate as "user-1" over SSH
        2. Run "sudo /bin/ls /root"
        3. Start tcpdump to capture ldap packets and run "sudo /bin/ls /root" multiple times again
    :expectedresults:
        1. User is logged into the host
        2. Command is successful, user is stored in negative cache for local users
        3. No ldap packets for "user-1" user resolution are sent
    :customerscenario: True
    """
    assert False


def test_failure_exception():
    """
    My custom string.

    :title: Failure exception
    :setup:
        1. Create local user "user-1"
        2. Add local rule to /etc/sudoers to allow all commands for "user-1"
        3. Enable sudo responder
        4. Set entry_negative_timeout to 0 to disable standard negative cache
        5. Start SSSD
    :steps:
        1. Authenticate as "user-1" over SSH
        2. Run "sudo /bin/ls /root"
        3. Start tcpdump to capture ldap packets and run "sudo /bin/ls /root" multiple times again
    :expectedresults:
        1. User is logged into the host
        2. Command is successful, user is stored in negative cache for local users
        3. No ldap packets for "user-1" user resolution are sent
    :customerscenario: True
    """
    raise ValueError("Error message")


@pytest.mark.skip(reason="Because.")
def test_skipped():
    """
    My custom string.

    :title: Skipped
    :setup:
        1. Create local user "user-1"
        2. Add local rule to /etc/sudoers to allow all commands for "user-1"
        3. Enable sudo responder
        4. Set entry_negative_timeout to 0 to disable standard negative cache
        5. Start SSSD
    :steps:
        1. Authenticate as "user-1" over SSH
        2. Run "sudo /bin/ls /root"
        3. Start tcpdump to capture ldap packets and run "sudo /bin/ls /root" multiple times again
    :expectedresults:
        1. User is logged into the host
        2. Command is successful, user is stored in negative cache for local users
        3. No ldap packets for "user-1" user resolution are sent
    :customerscenario: True
    """
    pass


def test_error_setup(error_setup):
    """
    My custom string.

    :title: Error setup
    :setup:
        1. Create local user "user-1"
        2. Add local rule to /etc/sudoers to allow all commands for "user-1"
        3. Enable sudo responder
        4. Set entry_negative_timeout to 0 to disable standard negative cache
        5. Start SSSD
    :steps:
        1. Authenticate as "user-1" over SSH
        2. Run "sudo /bin/ls /root"
        3. Start tcpdump to capture ldap packets and run "sudo /bin/ls /root" multiple times again
    :expectedresults:
        1. User is logged into the host
        2. Command is successful, user is stored in negative cache for local users
        3. No ldap packets for "user-1" user resolution are sent
    :customerscenario: True
    """
    pass


def test_error_teardown(error_teardown):
    """
    My custom string.

    :title: Error teardown
    :setup:
        1. Create local user "user-1"
        2. Add local rule to /etc/sudoers to allow all commands for "user-1"
        3. Enable sudo responder
        4. Set entry_negative_timeout to 0 to disable standard negative cache
        5. Start SSSD
    :steps:
        1. Authenticate as "user-1" over SSH
           Some other line
        2. Run "sudo /bin/ls /root"
        3. Start tcpdump to capture ldap packets and run "sudo /bin/ls /root" multiple times again
    :expectedresults:
        1. User is logged into the host
        2. Command is successful, user is stored in negative cache for local users
        3. No ldap packets for "user-1" user resolution are sent
    :customerscenario: True
    """
    pass


def test_error_setup_teardown(error_setup, error_teardown):
    """
    My custom string.

    :title: Error setup teardown
    :setup:
        1. Create local user "user-1"
        2. Add local rule to /etc/sudoers to allow all commands for "user-1"
        3. Enable sudo responder
        4. Set entry_negative_timeout to 0 to disable standard negative cache
        5. Start SSSD
    :steps:
        1. Authenticate as "user-1" over SSH
        2. Run "sudo /bin/ls /root"
        3. Start tcpdump to capture ldap packets and run "sudo /bin/ls /root" multiple times again
    :expectedresults:
        1. User is logged into the host
        2. Command is successful, user is stored in negative cache for local users
        3. No ldap packets for "user-1" user resolution are sent
    :customerscenario: True
    """
    pass
