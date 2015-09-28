This script produces csv output giving *useful* details of the usage
of ZFS snapshots.

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
filesystem, and shows how much space would be freed by deleting the
corresponding sequence of snapshots.

Output from this script:
(a) converts sizes shown into bytes
(b) strips any common prefix from snapshot names (e.g. "zfs-auto-snap")

Options could be added to enable/disable this, but I can't be bothered.

Example:
  zfs-snapshot-disk-usage-matrix.py local-fast-tank-machine0/Virtual-Machines/VirtualBox/vpn-linux-u14 | tee vpn-snapshot-usage.csv
