#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import sys
import time


def run_cmd(cmd, check=False):
    """Executes a shell command and logs output."""
    print(f"[Topology Setup] Running: {' '.join(cmd)}", flush=True)
    res = subprocess.run(cmd, check=check, capture_output=True, text=True)
    if res.stdout:
        print(f"[Topology Setup] stdout: {res.stdout.strip()}", flush=True)
    if res.stderr:
        print(f"[Topology Setup] stderr: {res.stderr.strip()}", flush=True)
    return res


def configure_topology():
    config_raw = os.environ.get("MENTORED_TOPOLOGY_CONFIG", "{}")
    if not config_raw or config_raw == "{}":
        print(
            "[Topology Setup] MENTORED_TOPOLOGY_CONFIG is empty. Skipping...",
            flush=True,
        )
        return

    try:
        config = json.loads(config_raw)
    except json.JSONDecodeError as err:
        print(
            f"[Topology Setup] ERROR: Invalid JSON in MENTORED_TOPOLOGY_CONFIG: {err}",
            flush=True,
        )
        sys.exit(1)

    underlay_dev = config.get("underlay", "eth0")
    default_dstport = str(config.get("dstport", 9999))
    socket.setdefaulttimeout(5.0)

    # --------------------------------------------------------------------------
    # 1. PROCESS BRIDGES
    # --------------------------------------------------------------------------
    bridges = config.get("bridges", [])
    for br in bridges:
        br_name = br.get("name")
        if not br_name:
            continue
        br_ip = br.get("ip")
        br_mtu = br.get("mtu", 1280)

        # Create bridge if missing
        res = run_cmd(["ip", "link", "show", br_name])
        if res.returncode != 0:
            print(f"[Bridge Setup] Creating bridge {br_name}", flush=True)
            run_cmd(
                ["ip", "link", "add", "name", br_name, "type", "bridge"],
                check=True,
            )

        if br_mtu:
            run_cmd(["ip", "link", "set", "dev", br_name, "mtu", str(br_mtu)])

        if br_ip:
            print(
                f"[Bridge Setup] Assigning IP {br_ip} to bridge {br_name}",
                flush=True,
            )
            run_cmd(["ip", "addr", "add", br_ip, "dev", br_name])

        run_cmd(["ip", "link", "set", br_name, "up"], check=True)

    # --------------------------------------------------------------------------
    # 2. PROCESS VXLAN INTERFACES
    # --------------------------------------------------------------------------
    vxlan_list = config.get("interfaces") or config.get("vxlans")
    if isinstance(vxlan_list, dict):
        vxlan_list = [vxlan_list]
    elif not vxlan_list and "interface" in config:
        vxlan_list = [config]
    elif not vxlan_list:
        vxlan_list = []

    for vx in vxlan_list:
        ifname = vx.get("interface", vx.get("name", "net1"))
        vni = vx.get("vni", 200)
        ip = vx.get("ip")
        remote_host = vx.get("remote_host") or vx.get("remote_ip")
        mtu = vx.get("mtu", 1280)
        dstport = str(vx.get("dstport", default_dstport))
        master_bridge = vx.get("bridge") or vx.get("master")

        if not remote_host:
            print(
                f"[VXLAN Setup] Skipping {ifname}: remote_host is required",
                flush=True,
            )
            continue

        # Resolve host via K8s DNS
        remote_ip = None
        print(
            f"[VXLAN Setup] Resolving IP for remote host: {remote_host}...",
            flush=True,
        )
        for attempt in range(30):
            try:
                remote_ip = socket.gethostbyname(remote_host)
                print(
                    f"[VXLAN Setup] Resolved {remote_host} -> {remote_ip}",
                    flush=True,
                )
                break
            except (socket.gaierror, socket.timeout) as err:
                print(
                    f"[VXLAN Setup] DNS attempt {attempt+1}/30 failed for {remote_host}: {err}",
                    flush=True,
                )
                time.sleep(2)

        if not remote_ip:
            print(
                f"[VXLAN Setup] Failed to resolve {remote_host}, skipping {ifname}",
                flush=True,
            )
            continue

        # Create VXLAN link if it doesn't exist
        res = run_cmd(["ip", "link", "show", ifname])
        if res.returncode != 0:
            print(
                f"[VXLAN Setup] Creating VXLAN {ifname} (VNI: {vni}, Remote: {remote_ip}, Dev: {underlay_dev}, Port: {dstport})",
                flush=True,
            )
            cmd_create = [
                "ip",
                "link",
                "add",
                ifname,
                "type",
                "vxlan",
                "id",
                str(vni),
                "remote",
                remote_ip,
                "dev",
                underlay_dev,
                "dstport",
                dstport,
            ]
            run_cmd(cmd_create, check=True)

        if mtu:
            run_cmd(["ip", "link", "set", "dev", ifname, "mtu", str(mtu)])

        # Handle slaving to bridge vs standalone IP assignment
        if master_bridge:
            res_br = run_cmd(["ip", "link", "show", master_bridge])
            if res_br.returncode != 0:
                print(
                    f"[VXLAN Setup] Creating master bridge {master_bridge} for slave {ifname}",
                    flush=True,
                )
                run_cmd(
                    [
                        "ip",
                        "link",
                        "add",
                        "name",
                        master_bridge,
                        "type",
                        "bridge",
                    ],
                    check=True,
                )
                run_cmd(
                    ["ip", "link", "set", master_bridge, "up"], check=True
                )

            print(
                f"[VXLAN Setup] Slaving {ifname} to bridge {master_bridge} (Skipping direct IP on {ifname})",
                flush=True,
            )
            run_cmd(
                ["ip", "link", "set", ifname, "master", master_bridge],
                check=True,
            )
        else:
            if ip:
                print(
                    f"[VXLAN Setup] Assigning IP {ip} to interface {ifname}",
                    flush=True,
                )
                run_cmd(["ip", "addr", "add", ip, "dev", ifname])

        run_cmd(["ip", "link", "set", ifname, "up"], check=True)

    socket.setdefaulttimeout(None)


if __name__ == "__main__":
    configure_topology()