#!/bin/bash

# CRDT Service Creator with Multiple Peer Support
# Usage: create_service.sh <node_name> <crdt_type> <sync_folder> <port> [peer1_host:peer1_port] [peer2_host:peer2_port] ...

set -e

NODE_NAME="${1:-node_a}"
CRDT_TYPE="${2:-g_counter}"
SYNC_FOLDER="${3:-/opt/crdt-cluster/sync_folder}"
PORT="${4:-9001}"
shift 4  # Remove the first 4 arguments

# Remaining arguments are peers
PEERS=("$@")

CONFIG_DIR="/opt/crdt-cluster/config"
SERVICE_DIR="/etc/systemd/system"

echo "Creating CRDT service..."
echo "Node: $NODE_NAME"
echo "Type: $CRDT_TYPE"
echo "Sync Folder: $SYNC_FOLDER"
echo "Port: $PORT"

# Create peers array in JSON format
PEERS_JSON=""
if [ ${#PEERS[@]} -gt 0 ]; then
    echo "Peers:"
    PEERS_JSON="["
    FIRST=true
    for peer in "${PEERS[@]}"; do
        # Split peer into host and port (format: host:port)
        IFS=':' read -r PEER_HOST PEER_PORT <<< "$peer"
        echo "  - $PEER_HOST:$PEER_PORT"
        
        if [ "$FIRST" = true ]; then
            FIRST=false
        else
            PEERS_JSON="$PEERS_JSON,"
        fi
        
        PEERS_JSON="$PEERS_JSON"$'\n      {'
        PEERS_JSON="$PEERS_JSON"$'\n        "host": "'"$PEER_HOST"'",'
        PEERS_JSON="$PEERS_JSON"$'\n        "port": '"$PEER_PORT"
        PEERS_JSON="$PEERS_JSON"$'\n      }'
    done
    PEERS_JSON="$PEERS_JSON"$'\n    ]'
else
    echo "Peers: None specified"
    PEERS_JSON="[]"
fi

# Create directories
mkdir -p "$CONFIG_DIR" "/opt/crdt-cluster/data" "/opt/crdt-cluster/logs" "$SYNC_FOLDER"

# Create configuration file
CONFIG_FILE="$CONFIG_DIR/${NODE_NAME}.json"
cat > "$CONFIG_FILE" << EOF
{
    "node_id": "$NODE_NAME",
    "host": "0.0.0.0",
    "port": $PORT,
    "sync_folder": "$SYNC_FOLDER",
    "peers": $PEERS_JSON,
    "state_file": "/opt/crdt-cluster/data/${NODE_NAME}_state.json",
    "logging_config": "/opt/crdt-cluster/config/logging_simple.conf",
    "sync_interval": 10,
    "scan_interval": 30,
    "crdt_type": "$CRDT_TYPE"
}
EOF

# Create service file
SERVICE_FILE="$SERVICE_DIR/crdt-${NODE_NAME}.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=CRDT $CRDT_TYPE Node $NODE_NAME
After=network.target
Wants=network.target

[Service]
Type=simple
User=crdt
Group=crdt
WorkingDirectory=/opt/crdt-cluster
ExecStartPre=/bin/bash -c 'mkdir -p /opt/crdt-cluster/{logs,data} $SYNC_FOLDER'
ExecStart=/usr/bin/python3 /opt/crdt-cluster/bin/crdt_service.py $CONFIG_FILE
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
TimeoutStopSec=30

Environment=PYTHONPATH=/opt/crdt-cluster/src
Environment=PYTHONUNBUFFERED=1

NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/crdt-cluster/data /opt/crdt-cluster/logs $SYNC_FOLDER

StandardOutput=journal
StandardError=journal
SyslogIdentifier=crdt-$NODE_NAME

[Install]
WantedBy=multi-user.target
EOF

# Set permissions (only on files we create, not recursive ownership)
chmod 644 "$CONFIG_FILE"
chmod 644 "$SERVICE_FILE"

echo ""
echo "Service created successfully!"
echo "Configuration: $CONFIG_FILE"
echo "Service file: $SERVICE_FILE"
echo ""
echo "To enable and start the service:"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable crdt-$NODE_NAME"
echo "  sudo systemctl start crdt-$NODE_NAME"
