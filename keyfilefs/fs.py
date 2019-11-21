#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import re

from fuse import FUSE, FuseOSError, Operations



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




class Passthrough(Operations):
    def __init__(self):
        self.uid = os.getuid()
        self.gid = os.getgid()

        self.entries = [
            "example-1",
            "example-2",
        ]

    def _split_path(self, path):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        if basename and not re.match("^[0-9a-zA-Z_\\-\\.]{1,256}$", basename):
            raise FuseOSError(errno.EINVAL)
        if dirname and dirname not in ["/", "/config"]:
            raise FuseOSError(errno.EACCES)
        return dirname, basename



    # Filesystem methods
    # ==================

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

    def getattr(self, path, fh=None):
        print("getattr", path, fh)
        attr = {
            "st_ctime": 0,
            "st_atime": 0,
            "st_mtime": 0,
            "st_uid"  : self.uid,
            "st_gid"  : self.gid,
            "st_mode" : 0,
            "st_nlink": 1,
            "st_size" : 0,
        }
        if path == "/config" or path == "/":
            attr["st_mode"] = STAT_FILETYPE.IFDIR | 0o700
            return attr

        attr["st_mode"] = STAT_FILETYPE.IFREG | 0o600
        attr["st_size"] = 64

        return attr

    def readdir(self, path, fh):
        dirname, basename = self._split_path(path)
        print("readdir", path, fh)
        yield "."
        yield ".."
        if path == "/":
            yield "config"
            for each in self.entries: yield each
        else:
            yield "option-1"
            yield "option-2"


    def statfs(self, path):
        print("statfs", path)
        raise FuseOSError(errno.EACCES)
        """return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))"""

    def unlink(self, path):
        print("unlink", path)
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        if dirname != "/" or basename not in self.entries:
            raise FuseOSError(errno.EACCES)


    def rename(self, old, new):
        print("rename", old, new)
#        return os.rename(self._full_path(old), self._full_path(new))

        

    def utimens(self, path, times=None):
#        return os.utime(self._full_path(path), times)
        return 0

    # File methods
    # ============

    def open(self, path, flags):
        dirname, basename = self._split_path(path)
        _flags = flags
        flags = [
            e for e in [
                s for s in dir(os) if s.startswith("O_")
            ]
            if getattr(os, e) & flags
        ]
        print("open", path, "%o" % _flags, flags)

        #if not basename in self.entries:
        #    raise FuseOSError(errno.ENOENT)

        #full_path = self._full_path(path)
        #return os.open(full_path, flags)
        return 3

    def create(self, path, mode, fi=None):
        return
        dirname, basename = self._split_path(path)
        print("create", path, mode, fi)

        if dirname != "/": raise FuseOSError(errno.EACCES)
        if basename == "config" or basename in self.entries:
            raise FuseOSError(errno.EEXIST)
        self.entries.append(basename)


    def read(self, path, length, offset, fh):
        print("read", path, length, offset, fh)
        return b"0" * length

    def write(self, path, buf, offset, fh):
        #if path != "/config": raise FuseOSError(errno.EACCES)
        print("write", path, buf, offset, fh)
        return len(buf)

    def truncate(self, path, length, fh=None):
        print("truncate", path, length)
        #if path != "/config": raise FuseOSError(errno.EACCES)

    def flush(self, path, fh):
        print("flush", path, fh)
        return
        return os.fsync(fh)

    def release(self, path, fh):
        print("release", path, fh)
        return True
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print("fsync", path, fdatasync, fh)
        return self.flush(path, fh)


def main(mountpoint):
    FUSE(Passthrough(), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[1])
