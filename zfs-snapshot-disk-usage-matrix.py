#!/usr/bin/env python3
"""Usage: zfs-snapshot-disk-usage-matrix.py <filesystem>

This script produces csv output giving useful details of the usage of
ZFS snapshots.

When you ask ZFS about the disk space used by snapshots, it really
only wants to tell you about how much space is being *uniquely* used
by individual snapshots. If a two adjacent snapshots use a Gigabyte of
space between them, but have only 1 Megabyte of space unique to each
of them, "zfs list" will tell you that each snapshot is consuming only
a *one* Megabyte of space. This is helpful if you're trying to work
out which snapshots to delete to free up diskspace.

If you use "zfs destroy -nv filesystem@snap1%snap2" ZFS *will*
actually tell you how much space the sequence of snapshots between
snap1 and snap2 is using.  This is much more useful for working out
which snapshots are using all the space.  In the example from the
previous paragraph, this would tell you that deleting both snapshots
together would 1.002 Gigabytes - obviously much more useful
information.

This script runs "zfs destroy -nv" for all pairs of snapshots in a
filesystem, and shows how much space you can free up by deleting the
corresponding sequence of snapshots.

Output from this script:
(a) converts sizes shown into bytes
(b) strips any common prefix from snapshot names (e.g. "zfs-auto-snap")

Options could be added to enable/disable this, but I can't be bothered.

Example:
  zfs-snapshot-disk-usage-matrix.py local-fast-tank-machine0/Virtual-Machines/VirtualBox/vpn-linux-u14 | tee vpn-snapshot-usage.csv

"""

import subprocess, sys, fcntl
from os.path import commonprefix

def strip_filesystem_name(snapshot_name):
    """Given the name of a snapshot, strip the filesystem part.

    We require (and check) that the snapshot name contains a single
    '@' separating filesystem name from the 'snapshot' part of the name.
    """
    assert snapshot_name.count("@")==1
    return snapshot_name.split("@")[1]

def maybe_ssh(host):
    if (host == 'localhost'):
        ## no need to ssh host @ start of command - empty string
        return []
    ##else
    ## will need the ssh in there
    return ['ssh', '-C', host]

def snapshots_in_creation_order(filesystem, host='localhost', strip_filesystem=False):
    "Return list of snapshots on FILESYSTEM in order of creation."
    result = []
    cmd = maybe_ssh(host) + ['zfs', 'list', '-r', '-t', 'snapshot',
            '-s', 'creation', '-o', 'name', filesystem]
    lines = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
            encoding='utf8').split('\n')
    snapshot_prefix = filesystem + "@"
    for line in lines:
        if line.startswith(snapshot_prefix):
            result.append(line)
    if strip_filesystem:
        return list(map(strip_filesystem_name, result))
    return result

def space_between_snapshots(filesystem, first_snap, last_snap, host='localhost'):
    "Space used by a sequence of snapshots."
    cmd = maybe_ssh(host) + ['zfs', 'destroy', '-nvp',
            '{}@{}%{}'.format(filesystem, first_snap, last_snap)]
    lines = subprocess.check_output(cmd, stderr=subprocess.STDOUT, encoding='utf8').split('\n')
    return lines[-2].split('\t')[-1]

def print_csv(lines):
    """Write out a list of lists as CSV.

    Not robust against odd input."""
    for line in lines:
        for item in line:
            if item != None:
                print(item, end='')
            print(",", end='')
        print()

def write_snapshot_disk_usage_matrix(filesystem, suppress_common_prefix=True):
    snapshot_names = snapshots_in_creation_order(filesystem, strip_filesystem=True)
    if suppress_common_prefix:
        suppressed_prefix_len = len(commonprefix(snapshot_names))
    else:
        suppressed_prefix_len = 0
    print_csv([[None]+[name[suppressed_prefix_len:] for name in snapshot_names]]) # Start with Column headers
    for end in range(len(snapshot_names)):
        this_line = [snapshot_names[end][suppressed_prefix_len:]]
        for start in range(len(snapshot_names)):
            if start <= end:
                start_snap = snapshot_names[start]
                end_snap = snapshot_names[end]
                space_used = space_between_snapshots(filesystem,
                                                     start_snap,
                                                     end_snap)
                this_line.append(space_used)
            else:
                this_line.append(None)
        ## Show line we've just done
        print_csv([this_line])

if __name__ == '__main__':
    write_snapshot_disk_usage_matrix(sys.argv[1])

# Useful for
# snapshots_in_creation_order('local-fast-tank-machine0/Virtual-Machines/VirtualBox/vpn-linux-u14')
# space_between_snapshots('local-fast-tank-machine0/Virtual-Machines/VirtualBox/vpn-linux-u14',
#                         'zfs-auto-snap_monthly-2015-03-18-2345',
#                         'zfs-auto-snap_frequent-2015-09-28-0245')
# write_snapshot_disk_usage_matrix('local-fast-tank-machine0/Virtual-Machines/VirtualBox/vpn-linux-u14')
