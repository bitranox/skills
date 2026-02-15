Cluster-Konfiguration
Umgebung: Proxmox VE 9.x (Enterprise/Community)
Nodes: 8 physische Knoten (pve-01 bis pve-08)
Quorum-Status: Kritisch (5/8 Knoten für Mehrheit erforderlich)
API-Zugriff: Über pvesh (lokal) oder Proxmox API (Remote)
Storage: [HIER STORAGE-TYP EINTRAGEN, z.B. Ceph, ZFS over iSCSI, NFS]

️ Sicherheits- & Schutzregeln (Safety Protocols)
Keine destruktiven Massenoperationen: Befehle, die mehr als einen Knoten gleichzeitig betreffen (Reboot, Shutdown, Bulk-VM-Stop), müssen explizit vom User bestätigt werden.
Quorum-Check: Vor jedem Knoten-Reboot oder Wartungsmodus prüfen: pvecm status. Operation abbrechen, wenn das Quorum bei Vollzugriff gefährdet ist
Backup-First: Vor Änderungen an VM-Konfigurationen oder Upgrades prüfen, ob ein aktuelles Backup existiert (vzdump).
Kein "Force"-Delete: Niemals --purge oder --force verwenden, ohne vorher die ID der Ressource doppelt zu validieren.
HA-Status: Bei Änderungen an HA-Clustern zuerst den HA-Manager Status prüfen (ha-manager status).

Management-Befehle (Cheat Sheet)
Cluster-Status: pvecm status / pvecm nodes
VM/LXC Liste (global): pvesh get /cluster/resources --type vm
Node-Metriken: pvesh get /nodes/{node}/status
Storage-Check: pvesh get /storage
Replikations-Status: pvesh get /cluster/replication
Service-Log: journalctl -u pve-cluster -f

Code- & Antwort-Stil
Antworten: Kurz, technisch präzise, Fokus auf CLI-Befehle (pvesh).
Fehlersuche: Bei Fehlern immer zuerst die Logs des betroffenen Knotens abfragen (/var/log/pveproxy/access.log).
JSON-Präferenz: Bei Datenabfragen bevorzugt pvesh --output-format json verwenden, um die Datenstruktur sauber zu analysieren.
Rollback-Plan: Jede vorgeschlagene Änderung muss (gedanklich) einen Rückkehrschritt enthalten.

Spezielle Workflows für 8 Knoten
Updates: Immer nacheinander (Rolling Updates). Node 1 -> Test -> Node 2.
Migration: Bei Load-Balancing-Vorschlägen die Ziel-Node-Auslastung (cpu, mem) vorher prüfen.
Netzwerk: Änderungen an interfaces immer mit ifreload -a vorbereiten, niemals direkt das Interface killen.
ID-Management: Vor dem Erstellen von VMs prüfen, ob die VM-ID im Bereich [DEIN BEREICH, z.B. 1000-2000] liegt, um Kollisionen mit bestehenden Clustern zu vermeiden.

Netzwerk-Diagnose (Cluster-Wide)
Interface-Status (API): pvesh get /nodes/{node}/network (zeigt Brücken, Bonds und IPs)
Bonding-Check (LACP/Failover): cat /proc/net/bonding/bondX (ersetze X durch Bond-ID, meist 0 oder 1)
OVS-Status (falls genutzt): ovs-vsctl show
MTU & Link-Speed: ip link show (wichtig für 10G/25G/40G Backplane-Checks)
VLAN-Brücken-Check: bridge vlan show
Netzwerk-Konfiguration testen: ifreload -a --test (vor der Aktivierung!)

