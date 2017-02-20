#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno

from fusepy.fuse import FUSE, FuseOSError, Operations
import imap
import config

from pprint import pprint

class Imap(Operations):
    emails = None
    account_config = None
    root = None
    _EMAIL_DIR = '.emails'

    def __init__(self, root, emails, account_config):
        self.root = root
        self.emails = emails
        self.account_config = account_config

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        pass
        #full_path = self._full_path(path)
        #if not os.access(full_path, mode):
            #raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        #full_path = self._full_path(path)
        #st = os.lstat(full_path)
        #d = dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
        #             'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

        #if 'whyMaximumNumberOfClientsReachedX.py' in path:
        #    pprint(d)
        #return d

        if 'README.md' in path:
            full_path = self._full_path(path)
            st = os.lstat(full_path)
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                         'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

        if 'plain-text.txt' in path or 'metadata.txt' in path or 'README' in path:
            return {
                'st_atime': 1485735362.1132069,
                'st_ctime': 1485727143.0372078,
                'st_gid': 1000,
                'st_mode': 33204, # normal?
                #'st_mode': 41471, # symlink
                'st_mtime': 1485727143.0372078,
                'st_nlink': 1,
                'st_size': 12000,
                'st_uid': 1000
            }

        if '.txt' in path:
            return {
                'st_atime': 1485735362.1132069,
                'st_ctime': 1485727143.0372078,
                'st_gid': 1000,
                #'st_mode': 33204, # normal?
                'st_mode': 41471, # symlink
                'st_mtime': 1485727143.0372078,
                'st_nlink': 1,
                'st_size': 12000,
                'st_uid': 1000
            }
        #if self.account_config.email_address in path:
        return { # Directory
            'st_atime': 1485738550.6692064,
            'st_ctime': 1485738570.1532063,
            'st_gid': 1000,
            'st_mode': 16893,
            'st_mtime': 1485738570.1532063,
            'st_nlink': 2,
            'st_size': 4096,
            'st_uid': 1000
            }

        #else:
        #    d = { # Directory
        #        'st_atime': 1485738550.6692064,
        #        'st_ctime': 1485738570.1532063,
        #        'st_gid': 1000,
        #        'st_mode': 16893,
        #        'st_mtime': 1485738570.1532063,
        #        'st_nlink': 2,
        #        'st_size': 4096,
        #        'st_uid': 1000
        #    }
        #return d

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']

        if '/' == path:
            dirents.append(self.account_config.email_address)
            dirents.extend(os.listdir(full_path))
        elif '/' + self.account_config.email_address == path:
            dirents.append(self._EMAIL_DIR)
            dirents.append('plain-text')
        elif '/' + self.account_config.email_address + '/plain-text' == path:
            email_titles = []
            for key, email in self.emails.iteritems():
                email_titles.append('%s [from %s] (%s).txt' % (email['subject'], email['from'], key))
            dirents.extend(email_titles)
        elif '/' + self.account_config.email_address + '/' + self._EMAIL_DIR in path:
            keys = self.emails.keys()
            dir_no = path.split('/')[-1]

            if '/' + self.account_config.email_address + '/' + self._EMAIL_DIR != path:
                pprint(dir_no)
                dirents.append('plain-text.txt')
                dirents.append('metadata.txt')
            else:
                dirents.extend(keys)

        for r in dirents:
            yield r

    def readlink(self, path):
        return '/sdfgsdgsdfgWWW'
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        d = dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))
        return d

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        print 345
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        return 1
        #print 222222222
        #full_path = self._full_path(path)
        #return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        print 8898
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        if 'README.md' in path:
            os.lseek(fh, offset, os.SEEK_SET)
            return os.read(fh, length)

        dir_no = path.split('/')[3].split('/')[-1]
        print '[------------]', dir_no

        if 'plain-text.txt' in path:
            return self.emails[dir_no]['plain_text']
        return 'subject: ' + self.emails[dir_no]['subject']
        print 5674
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        print 234234
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        print 777
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    #def flush(self, path, fh):
        #return 1
        #print 21212
        #return os.fsync(fh)

    def release(self, path, fh):
        return None
        print 9999
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print 8888
        return self.flush(path, fh)


def main(mount_point):
    root = 'in/'
    account_config = config.load()
    emails = imap.get_inbox_listing(account_config)
    FUSE(Imap(root, emails, account_config), mount_point, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[1])
