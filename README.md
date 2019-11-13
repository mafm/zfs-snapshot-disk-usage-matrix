# *Useful* ZFS snapshot disk space usage accounting

Confusion and frustration over ZFS snapshots disk space usage seems to be common.

This script produces _useful_ disk space accounting for snapshots on a ZFS filesystem.

## The problem

When you ask ZFS about the disk space used by snapshots, it really
only wants to tell you about how much space is being *uniquely* used
by individual snapshots. If two adjacent snapshots:
- both reference a shared Gigabyte of space that is not referenced by any other snapshot, but
- each uniquely reference only 1 Megabyte of space,

"zfs list" will tell you that each snapshot is consuming only
a *one* Megabyte of space. This is *not* helpful if you're trying to work
out which snapshots to delete to free up diskspace.

Although the example scenario might seem unlikely, it seems to be a common cause of confusion and frustration.
In the archives of the zfs-discuss mailing list, there's recurring advice that the best way out of the situation is to blindly start deleting snapshots and see how much disk space comes back.
- [[zfs-discuss] ZFS snapshot used space question](http://markmail.org/thread/msfiihbjjtsphypr)
- [[zfs-discuss] What's eating my disk space? Missing snapshots?](http://markmail.org/thread/2btnhnd3d3ctojx3)
- [[zfs-discuss] Disk space usage of zfs snapshots and filesystems - my math doesn't add up](http://markmail.org/thread/o5pffx7ltfpyu7rj)

## A solution

If you use "zfs destroy -nv filesystem@snap1%snap2" ZFS *will*
actually tell you how much space the sequence of snapshots between
snap1 and snap2 is using.  This is more useful for working out
which snapshots are consuming disk space. In the example from the
previous paragraph, this would inform you that deleting *both* snapshots
together would free 1.002 Gigabytes - clearly more useful than telling
you that freeing either one individually would free one Megabyte.

## This script

This script runs "zfs destroy -nv" for all pairs of snapshots in a
filesystem, and shows how much space would be freed by deleting the
corresponding sequence of snapshots. It produces a csv-formatted matrix
with row and column headers. If you send the output to a file, it
can be read using Excel or some other spreadsheet-type software to see
exactly which snapshots are using the space.

Output from this script:
- converts sizes reported by ZFS into bytes
- strips any common prefix from snapshot names (e.g. "zfs-auto-snap")

Options could be added to enable/disable this, but I can't be bothered right now.

There may be an easier way of doing this. If you know about it, please tell me.

Example:

> `zfs-snapshot-disk-usage-matrix.py local-fast-tank-machine0/Virtual-Machines/VirtualBox/vpn-linux-u14 | tee vpn-snapshot-usage.csv`

