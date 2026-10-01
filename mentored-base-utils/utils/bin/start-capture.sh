#!/usr/bin/env bash
set -e

CAPTURE_DIR="${CAPTURE_DIR:-/app/results}"
CAPTURE_FILE="${CAPTURE_FILE:-packets.pcapng}"
CAPTURE_IFACE="${CAPTURE_IFACE:-any}"
CAPTURE_FILTER="${CAPTURE_FILTER:-}"

mkdir -p "$CAPTURE_DIR"

if command -v mentored-registry-action >/dev/null 2>&1; then
    mentored-registry-action -a tshark -o "$CAPTURE_DIR" -n "Starting packet capture"
fi

echo "[MONITORING] Starting dumpcap on interface '${CAPTURE_IFACE}' -> ${CAPTURE_DIR}/${CAPTURE_FILE}"

DUMPCAP_ARGS=("-i" "$CAPTURE_IFACE" "-w" "${CAPTURE_DIR}/${CAPTURE_FILE}")

if [ -n "$CAPTURE_FILTER" ]; then
    DUMPCAP_ARGS+=("-f" "$CAPTURE_FILTER")
fi

# Run dumpcap in the background
dumpcap "${DUMPCAP_ARGS[@]}" >/dev/null 2>&1 &
echo $! > /var/run/dumpcap.pid