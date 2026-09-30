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
    dstport = str(config.get("dstport", 9999))
    base_vni = int(config.get("vni", 200))
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
            run_cmd(["ip", "link", "add", "name", br_name, "type", "bridge"], check=True)

        # Set forward_delay to 0 so ports go to FORWARDING state immediately
        run_cmd(["ip", "link", "set", "dev", br_name, "type", "bridge", "forward_delay", "0", "stp_state", "0"])

        if br_mtu:
            run_cmd(["ip", "link", "set", "dev", br_name, "mtu", str(br_mtu)])

        if br_ip:
            print(f"[Bridge Setup] Assigning IP {br_ip} to bridge {br_name}", flush=True)
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

    used_vnis = set()

    for idx, vx in enumerate(vxlan_list):
        ifname = vx.get("interface", vx.get("name", f"vxlan{idx}"))
        
        # Determine unique VNI per interface
        requested_vni = vx.get("vni")
        if requested_vni is not None and int(requested_vni) not in used_vnis:
            vni = int(requested_vni)
        else:
            vni = base_vni + idx
        used_vnis.add(vni)

        ip = vx.get("ip")
        remote_host = vx.get("remote_host") or vx.get("remote_ip")
        mtu = vx.get("mtu", 1280)
        link_dstport = str(vx.get("dstport", dstport))
        master_bridge = vx.get("bridge") or vx.get("master")

        if not remote_host:
            print(
                f"[VXLAN Setup] Skipping {ifname}: remote_host is required",
                flush=True,
            )
            continue

        # Resolve remote host IP
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

        # Create Point-to-Point VXLAN link with unique VNI
        res = run_cmd(["ip", "link", "show", ifname])
        if res.returncode != 0:
            print(
                f"[VXLAN Setup] Creating Point-to-Point VXLAN {ifname} (VNI: {vni}, Remote: {remote_ip}, Dev: {underlay_dev}, Port: {link_dstport})",
                flush=True,
            )
            cmd_create = [
                "ip", "link", "add", ifname,
                "type", "vxlan",
                "id", str(vni),
                "dev", underlay_dev,
                "dstport", link_dstport,
                "remote", remote_ip,
                "learning"
            ]
            run_cmd(cmd_create, check=True)

        if mtu:
            run_cmd(["ip", "link", "set", "dev", ifname, "mtu", str(mtu)])

        # Handle slaving to bridge
        if master_bridge:
            res_br = run_cmd(["ip", "link", "show", master_bridge])
            if res_br.returncode != 0:
                print(
                    f"[VXLAN Setup] Creating master bridge {master_bridge} for slave {ifname}",
                    flush=True,
                )
                run_cmd(["ip", "link", "add", "name", master_bridge, "type", "bridge"], check=True)
                run_cmd(["ip", "link", "set", "dev", master_bridge, "type", "bridge", "forward_delay", "0", "stp_state", "0"])
                run_cmd(["ip", "link", "set", master_bridge, "up"], check=True)

            print(
                f"[VXLAN Setup] Slaving {ifname} to bridge {master_bridge}",
                flush=True,
            )
            run_cmd(["ip", "link", "set", ifname, "master", master_bridge], check=True)
            run_cmd(["bridge", "link", "set", "dev", ifname, "learning", "on", "flood", "on"], check=False)
        else:
            if ip:
                run_cmd(["ip", "addr", "add", ip, "dev", ifname])

        run_cmd(["ip", "link", "set", ifname, "up"], check=True)

    socket.setdefaulttimeout(None)


if __name__ == "__main__":
    configure_topology()