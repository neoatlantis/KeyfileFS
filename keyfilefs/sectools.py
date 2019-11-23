# -*- coding: utf-8 -*-

import os
import pwd
import grp
import sys
import resource
import ctypes
import ctypes.util


try:
    _LIBC = ctypes.CDLL(ctypes.util.find_library("c"))
except:
    class _LIBC(object):
        def mlockall(self, x):
            return -1




def cap_enter():
    """
    Tries to enter a capability mode sandbox through the cap_enter
    call. Use it when everything the process will be doing afterwards
    is pure computation & usage of already opened file descriptors.

    Works on FreeBSD, see capsicum(4).

    Returns True if successful, False otherwise.
    """
    try:
        return _LIBC.cap_enter() != -1
    except:
        return False


def disallow_swap():
    """
    Tries to disallow memory swapping through the mlockall call
    in order to prevent secrets from leaking to the disk.

    Returns True if successful, False otherwise.
    """
    return _LIBC.mlockall(2) != -1


def disallow_core_dumps():
    """
    Disallows core dumps through the setrlimit call
    in order to prevent secrets from leaking to the disk.
    """
    return resource.setrlimit(resource.RLIMIT_CORE, [0, 0])
