from ctypes import *
import os
from enum import IntFlag
import errno

libc = cdll.LoadLibrary('libc.so.6')

class CloneFlag(IntFlag):
    VM = 0x00000100   #/* set if VM shared between processes */
    FS = 0x00000200    #/* set if fs info shared between processes */
    FILES = 0x00000400    #/* set if open files shared between processes */
    SIGHAND = 0x00000800    #/* set if signal handlers and blocked signals shared */
    PTRACE = 0x00002000    #/* set if we want to let tracing continue on the child too */
    VFORK = 0x00004000    #/* set if the parent wants the child to wake it up on mm_release */
    PARENT = 0x00008000    #/* set if we want to have the same parent as the cloner */
    THREAD = 0x00010000    #/* Same thread group? */
    NEWNS = 0x00020000    #/* New mount namespace group */
    SYSVSEM = 0x00040000    #/* share system V SEM_UNDO semantics */
    SETTLS = 0x00080000    #/* create a new TLS for the child */
    PARENT_SETTID = 0x00100000    #/* set the TID in the parent */
    CHILD_CLEARTID = 0x00200000    #/* clear the TID in the child */
    DETACHED = 0x00400000    #/* Unused, ignored */
    UNTRACED = 0x00800000    #/* set if the tracing process can't force CLONE_PTRACE on this clone */
    CHILD_SETTID = 0x01000000    #/* set the TID in the child */
    NEWCGROUP = 0x02000000    #/* New cgroup namespace */
    NEWUTS = 0x04000000    #/* New utsname namespace */
    NEWIPC = 0x08000000    #/* New ipc namespace */
    NEWUSER = 0x10000000    #/* New user namespace */
    NEWPID = 0x20000000    #/* New pid namespace */
    NEWNET = 0x40000000    #/* New network namespace */
    IO = 0x80000000    #/* Clone io context */

class MountFlag(IntFlag):
    RDONLY = 1
    NOSUID = 2
    NODEV = 4
    NOEXEC = 8
    SYNCHRONOUS = 16
    REMOUNT = 32
    MANDLOCK = 64
    DIRSYNC = 128
    NOATIME = 1024
    NODIRATIME = 2048
    BIND = 4096
    MOVE = 8192
    REC = 16384
    SILENT = 32768
    POSIXACL = 1<<16
    UNBINDABLE = 1<<17
    PRIVATE = 1<<18
    SLAVE = 1<<19
    SHARED = 1<<20
    RELATIME = 1<<21
    KERNMOUNT = 1<<22
    I_VERSION = 1<<23
    STRICTATIME = 1<<24
    LAZYTIME = 1<<25

def ptr_addr(ptr):
    return ptr.value

def ptr_offset(ptr, offset):
    return type(ptr)(ptr_addr(ptr) + offset)

def malloc(size):
    return c_void_p(libc.malloc(size))

def clone(entry_func, flags=0, stack_size=4096):
    entry_point = CFUNCTYPE(c_int)(entry_func)
    child_stack = malloc(stack_size)
    stack_top_ptr = ptr_offset(child_stack, stack_size)
    ret_code = libc.clone(entry_point, stack_top_ptr, flags)

    # parent and child process does not share address space
    # unless CLONE_VM is set
    libc.free(child_stack)

    if ret_code == -1:
        err = get_errno()
        if err == 0:
            # do not have CAP_SYS_ADMIN
            err = errno.EPERM
        raise OSError(err, 'clone failed {}:'.format(flags, os.strerror(err)))
    return ret_code

libc.mount.argtypes = (c_char_p, c_char_p, c_char_p, c_ulong, c_char_p)
def mount(source, target, fs, flags, data):
    source = source.encode()
    target = target.encode()
    fs = fs.encode()
    ret = libc.mount(source, target, fs, flags, data)
    if ret < 0:
        err = get_errno()
        if err == 0:
            # do not have CAP_SYS_ADMIN
            err = errno.EPERM
        raise OSError(errno, 'Error mounting {} {} {} {} {}: {}'.format(source, target, fs, flags, data, os.strerror(err)))

def switch_root(target):
    os.chdir(target)
    libc.pivot_root(b'.', None)
    os.chroot('.')

def mkdir_and_mount(source, target, fs_type, flags, data):
    if not os.path.exists(target):
        print(target)
        os.mkdir(target)
    mount(source, target, fs_type, flags, data)

import time
def entry_point():
    os.close
    time.sleep(1)
    switch_root('./rootfs')
    print('uid:', os.getuid())
    print('pid:', os.getpid())
    mkdir_and_mount('proc', '/proc', 'proc', MountFlag.NOSUID|MountFlag.NODEV|MountFlag.NOEXEC, None)
    mkdir_and_mount('sys', '/sys', 'sysfs', MountFlag.NOSUID|MountFlag.NODEV|MountFlag.NOEXEC, None)
    mkdir_and_mount('dev', '/dev', 'tmpfs', MountFlag.NOSUID|MountFlag.NOEXEC, b'size=100k')
    #mkdir_and_mount('devpts', '/dev/pts', 'devpts', MountFlag.NOSUID|MountFlag.NOEXEC, None)
    mkdir_and_mount('run', '/run', 'tmpfs', MountFlag.NOSUID|MountFlag.NODEV, None)
    mkdir_and_mount('tmp', '/tmp', 'tmpfs', MountFlag.NOSUID|MountFlag.NODEV, None)
    os.execv('/busybox', ['/busybox', 'ash'])
    return 0

child = clone(entry_point, CloneFlag.NEWNS|CloneFlag.NEWUSER|CloneFlag.NEWPID|CloneFlag.NEWUTS|CloneFlag.NEWIPC|CloneFlag.NEWNET)

open('/proc/{}/uid_map'.format(child), 'w').write('0 {} 1\n'.format(os.getuid(), os.getuid()))
time.sleep(1024)