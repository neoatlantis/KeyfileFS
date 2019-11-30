#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import re
import hashlib

from fuse import FUSE, FuseOSError, Operations

from .fs_config import KeyfileFSConfig
from .fs_keyfiles import KeyfileFSKeyfiles
from .constants import *





class STAT_FILETYPE:
    # https://github.com/torvalds/linux/blob/master/include/uapi/linux/stat.h

    #define S_IFLNK	 0120000
    #define S_IFREG  0100000
    #define S_IFBLK  0060000
    #define S_IFDIR  0040000
    #define S_IFCHR  0020000
    #define S_IFIFO  0010000
    IFREG = 0o0100000
    IFDIR = 0o0040000

class STAT_PERMISSIONS:
    U_R = 0o400
    U_W = 0o200
    U_X = 0o100
    G_R = 0o040
    G_W = 0o020
    G_X = 0o010
    O_R = 0o004
    O_W = 0o002
    O_X = 0o001


def calculateMasterSecret(filepath):
    digester = hashlib.sha512()
    with open(filepath, "rb") as f:
        for i in range(0, 16):
            data = f.read(65536)
            if data:
                digester.update(data)
            else:
                break
    return digester.digest()



class KeyfileFSOperations(Operations):

    def __init__(self):
        self.uid = os.getuid()
        self.gid = os.getgid()

        self.saltsFromDirectory = []

        self._secretRaw = b""
        self._secretKeyfile = b""
        self.secret = b""

        self.modules = {
            "config":   KeyfileFSConfig(),
            "keyfiles": KeyfileFSKeyfiles(self),
        }

        self.released = False # if keyfile is released for reading

    def _updateSecret(self):
        self.secret = hashlib.sha512(
            self._secretRaw + self._secretKeyfile).digest()

    def setSaltsFromDirectory(self, directory):
        salts = os.listdir(directory)
        salts = [
            e
            for e in salts
            if os.path.isfile(os.path.join(directory, e)) and \
                re.match(REGEX_FILENAME_RULE, e)
        ]
        self.saltsFromDirectory = salts
        self.modules["keyfiles"].updateSalts()

    def setSecret(self, secret):
        # Sets the secret directly.
        self._secretRaw = secret
        self._updateSecret()

    def setKeyfile(self, keyfile):
        # Sets the secret from a given master keyfile
        self._secretKeyfile = calculateMasterSecret(keyfile)
        self._updateSecret()

    def setRelease(self, released):
        self.released = released

    def _split_path(self, path):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        if basename and not re.match(REGEX_FILENAME_RULE, basename):
            raise FuseOSError(errno.EINVAL)
        if dirname and not (dirname == "/" or dirname[1:] in self.modules):
            raise FuseOSError(errno.EACCES)
        return dirname, basename


    def access(self, path, mode):
        dirname, basename = self._split_path(path)
        print("access", path, mode)

    def readlink(self, path): raise FuseOSError(errno.EPERM)
    def mknod(self, path, mode, dev): raise FuseOSError(errno.EPERM)
    def rmdir(self, path): raise FuseOSError(errno.EPERM)
    def mkdir(self, path, mode): raise FuseOSError(errno.EPERM)
    def symlink(self, name, target): raise FuseOSError(errno.EPERM)
    def link(self, target, name): raise FuseOSError(errno.EPERM)
    def chmod(self, path, mode): raise FuseOSError(errno.EPERM)
    def chown(self, path, uid, gid): raise FuseOSError(errno.EPERM)
    def unlink(self, path): raise FuseOSError(errno.EPERM)
    def rename(self, old, new): raise FuseOSError(errno.EPERM)
    def write(self, path, buf, offset, fh): raise FuseOSError(errno.EPERM)
    def truncate(self, path, length, fh=None): raise FuseOSError(errno.EPERM)
    def statfs(self, path): raise FuseOSError(errno.EACCES)


    def getattr(self, path, fh=None):
        dirname, basename = self._split_path(path)
        attr = {
            "st_ctime": 0,
            "st_atime": 0,
            "st_mtime": 0,
            "st_uid"  : self.uid,
            "st_gid"  : self.gid,
            "st_mode" : 0,
            "st_nlink": 1,
            "st_size" : 1,
        }
        dirname = dirname[1:]
        print("getattr", "path=", path, "dirname=", dirname, "basename=", basename)

        if dirname == "": #  "/" actually
            if basename != "" and basename in self.modules:
                attr["st_mode"] = STAT_FILETYPE.IFDIR | 0o700
            elif basename == "":
                attr["st_mode"] = STAT_FILETYPE.IFDIR | 0o700
            else:
                raise FuseOSError(errno.ENOENT)
        elif dirname in self.modules:
            attr["st_mode"] = STAT_FILETYPE.IFREG | 0o600
            updates = self.modules[dirname].getattr(basename)
            for each in updates: attr[each] = updates[each]
        else:
            raise FuseOSError(errno.EPERM)

        #print(attr)
        return attr

    def readdir(self, path, fh):
        dirname, basename = self._split_path(path)
        print("readdir", path, fh)
        yield "."
        yield ".."
        
        if path == "/":
            for each in self.modules: # subdir: config/, keyfiles/
                yield each
        else:
            if dirname == "/" and basename in self.modules:
                for each in self.modules[basename].readdir():
                    yield each
            else:
                raise FuseOSError(errno.EPERM)




        

    def utimens(self, path, times=None):
#        return os.utime(self._full_path(path), times)
        return 0

    # File methods
    # ============

    def open(self, path, flags): return 0
    def create(self, path, mode, fi=None): return 0


    def read(self, path, length, offset, fh):
        print("read", path, length, offset, fh)
        dirname, basename = self._split_path(path)
        if dirname[1:] in self.modules:
            if not self.released:
                raise FuseOSError(errno.EPERM)
            return self.modules[dirname[1:]].read(basename, length, offset)
        raise FuseOSError(errno.ENOENT)



    def flush(self, path, fh):
        print("flush", path, fh)
        return

    def release(self, path, fh):
        print("release", path, fh)
        return True

    def fsync(self, path, fdatasync, fh):
        print("fsync", path, fdatasync, fh)
        return


def mountKeyfileFS(operations, mountpoint, nothreads=True, foreground=True):
    assert isinstance(operations, KeyfileFSOperations)
    FUSE(operations, mountpoint, nothreads=nothreads, foreground=foreground)
    return operations

if __name__ == '__main__':
    mountKeyfileFS(
        mountpoint=sys.argv[1],
        secret=b"abc",
        saltProvider=["file-1", "file-2"],
    )
