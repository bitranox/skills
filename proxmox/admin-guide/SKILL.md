---
name: proxmox-admin-guide
description: >-
  Use when configuring, managing, or troubleshooting Proxmox VE -
  installation, host administration, clusters, VMs, containers,
  storage, Ceph, SDN, firewall, user management, HA, backups,
  notifications, and CLI tools. Covers Proxmox VE 9.1.2.
---

# Proxmox VE Administration Guide (Release 9.1.2)

Reference documentation for Proxmox VE administration extracted from
the official admin guide. Use the Read tool to load files relevant
to the current task.

## Which File Do I Need?

| I need to...                    | Read                                        |
|---------------------------------|---------------------------------------------|
| Install or upgrade Proxmox VE   | `ch02-installation.md`                      |
| Configure package repositories  | `ch03-host-admin/package-repositories.md`   |
| Set up networking               | `ch03-host-admin/network-configuration.md`  |
| Manage ZFS on the host          | `ch03-host-admin/zfs.md`                    |
| Manage LVM on the host          | `ch03-host-admin/lvm.md`                    |
| Configure certificates / ACME   | `ch03-host-admin/certificate-management.md` |
| Use the web GUI                 | `ch04-gui.md`                               |
| Create or manage a cluster      | `ch05-cluster-manager/_index.md`            |
| Understand pmxcfs               | `ch06-pmxcfs.md`                            |
| Add or configure storage        | `ch07-storage/_index.md`                    |
| Deploy Ceph                     | `ch08-ceph/_index.md`                       |
| Set up storage replication      | `ch09-storage-replication.md`               |
| Create or manage VMs            | `ch10-qemu/_index.md`                       |
| Create or manage containers     | `ch11-containers/_index.md`                 |
| Configure SDN                   | `ch12-sdn/_index.md`                        |
| Configure the firewall          | `ch13-firewall/_index.md`                   |
| Manage users and permissions    | `ch14-user-management/_index.md`            |
| Set up High Availability        | `ch15-high-availability/_index.md`          |
| Back up or restore VMs/CTs      | `ch16-backup-restore/_index.md`             |
| Configure notifications         | `ch17-notifications.md`                     |
| Look up a CLI command           | `appendix-a-cli/_index.md`                  |
| Check firewall macros           | `appendix-f-firewall-macros.md`             |
| Understand config file format   | `appendix-c-config-files.md`                |
| Schedule jobs (calendar events) | `appendix-d-calendar-events.md`             |

---

## Chapters

| File                                                  | Description                                                                 |
|-------------------------------------------------------|-----------------------------------------------------------------------------|
| [Introduction](ch01-introduction.md)                  | PVE overview, features, getting help                                        |
| [Installation](ch02-installation.md)                  | System requirements, installer, Debian install                              |
| [Host System Admin](ch03-host-admin/_index.md)        | Repos, network, ZFS, LVM, BTRFS, certs, bootloader                          |
| [Graphical User Interface](ch04-gui.md)               | Web GUI features, login, panels, tags                                       |
| [Cluster Manager](ch05-cluster-manager/_index.md)     | Create/join clusters, quorum, corosync, migration                           |
| [Cluster File System](ch06-pmxcfs.md)                 | pmxcfs, file layout, recovery                                               |
| [Storage](ch07-storage/_index.md)                     | Storage types, backends (Dir, NFS, CIFS, PBS, ZFS, LVM, iSCSI, Ceph, BTRFS) |
| [Ceph Cluster](ch08-ceph/_index.md)                   | Ceph installation, monitors, OSDs, pools, CRUSH, CephFS                     |
| [Storage Replication](ch09-storage-replication.md)    | ZFS-based replication, scheduling                                           |
| [QEMU/KVM VMs](ch10-qemu/_index.md)                   | VM settings, hardware, migration, cloud-init, PCI passthrough               |
| [Containers](ch11-containers/_index.md)               | LXC containers, images, settings, security, storage                         |
| [Software-Defined Network](ch12-sdn/_index.md)        | Zones, VNets, controllers, fabrics, IPAM, DHCP                              |
| [Firewall](ch13-firewall/_index.md)                   | Rules, security groups, IP sets, nftables                                   |
| [User Management](ch14-user-management/_index.md)     | Users, groups, auth realms, 2FA, permissions                                |
| [High Availability](ch15-high-availability/_index.md) | HA resources, fencing, recovery, scheduling                                 |
| [Backup and Restore](ch16-backup-restore/_index.md)   | Backup modes, jobs, retention, restore                                      |
| [Notifications](ch17-notifications.md)                | Targets, matchers, events, templates                                        |
| [Service Daemons](ch18-service-daemons.md)            | pvedaemon, pveproxy, pvestatd, spiceproxy                                   |
| [CLI Tools](ch19-cli-tools.md)                        | pvesubscription, pveperf, pvesh                                             |
| [FAQ](ch20-faq.md)                                    | Frequently asked questions                                                  |
| [Bibliography](ch21-bibliography.md)                  | Books and references                                                        |

---

## CLI Reference (Appendix A)

| File                                                    | Tool              | Description                    |
|---------------------------------------------------------|-------------------|--------------------------------|
| [General](appendix-a-cli/general-and-format-options.md) | -                 | General CLI and format options |
| [pvesm](appendix-a-cli/pvesm.md)                        | `pvesm`           | Storage Manager                |
| [pvesubscription](appendix-a-cli/pvesubscription.md)    | `pvesubscription` | Subscription Manager           |
| [pveperf](appendix-a-cli/pveperf.md)                    | `pveperf`         | Benchmark Script               |
| [pveceph](appendix-a-cli/pveceph.md)                    | `pveceph`         | Ceph Services Manager          |
| [pvenode](appendix-a-cli/pvenode.md)                    | `pvenode`         | Node Management                |
| [pvesh](appendix-a-cli/pvesh.md)                        | `pvesh`           | API Shell                      |
| [qm](appendix-a-cli/qm.md)                              | `qm`              | QEMU/KVM VM Manager            |
| [qmrestore](appendix-a-cli/qmrestore.md)                | `qmrestore`       | Restore VM Backups             |
| [pct](appendix-a-cli/pct.md)                            | `pct`             | Container Toolkit              |
| [pveam](appendix-a-cli/pveam.md)                        | `pveam`           | Appliance Manager              |
| [pvecm](appendix-a-cli/pvecm.md)                        | `pvecm`           | Cluster Manager                |
| [pvesr](appendix-a-cli/pvesr.md)                        | `pvesr`           | Storage Replication            |
| [pveum](appendix-a-cli/pveum.md)                        | `pveum`           | User Manager                   |
| [vzdump](appendix-a-cli/vzdump.md)                      | `vzdump`          | Backup Utility                 |
| [ha-manager](appendix-a-cli/ha-manager.md)              | `ha-manager`      | HA Manager                     |

---

## Appendices

| File                                              | Description                                          |
|---------------------------------------------------|------------------------------------------------------|
| [Service Daemons](appendix-b-service-daemons.md)  | Daemon CLI reference (pve-firewall, pvedaemon, etc.) |
| [Configuration Files](appendix-c-config-files.md) | datacenter.cfg format and options                    |
| [Calendar Events](appendix-d-calendar-events.md)  | Schedule format specification                        |
| [QEMU vCPU List](appendix-e-vcpu-list.md)         | Intel and AMD CPU types                              |
| [Firewall Macros](appendix-f-firewall-macros.md)  | Predefined firewall macro definitions                |
| [Markdown Primer](appendix-g-markdown-primer.md)  | Markdown syntax for PVE notes                        |
| [License](appendix-h-license.md)                  | GNU Free Documentation License                       |

