#!/bin/bash
# Engram One-Command Installer
set -e

ENGRAM_DIR="$HOME/.engram"
ENGINE_URL="https://get.useengram.com/engram.tar.gz"

echo "=== Engram Installation ==="

# 1. Prepare directory
mkdir -p "$ENGRAM_DIR"

# 2. Download and extract
echo "Downloading Engram runtime..."
# If we are running as a one-liner, we need to download the source
if [ ! -f "engram.tar.gz" ]; then
    echo "Local tarball not found, downloading from source..."
    # You can point this to the GitHub repo's main branch tarball or a specific release
    curl -fsSL "https://github.com/kwstx/engram_translator/archive/refs/heads/main.tar.gz" -o engram.tar.gz
    tar -xzf engram.tar.gz --strip-components=1 -C "$ENGRAM_DIR"
    rm engram.tar.gz
else
    tar -xzf engram.tar.gz -C "$ENGRAM_DIR"
fi

# 3. Create CLI wrapper
cat <<EOF > "$ENGRAM_DIR/engram"
#!/bin/bash
python3 "$ENGRAM_DIR/app/cli.py" "\$@"
EOF
chmod +x "$ENGRAM_DIR/engram"

# Link to bin
mkdir -p "$HOME/bin"
ln -sf "$ENGRAM_DIR/engram" "$HOME/bin/engram"
export PATH="\$PATH:\$HOME/bin"

# 4. Initialize configuration
echo "Initializing Engram config..."
"$ENGRAM_DIR/engram" init

# 5. Setup persistent daemon (systemd or launchd)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Creating systemd service..."
    cat <<EOF | sudo tee /etc/systemd/system/engram.service
[Unit]
Description=Engram Daemon Runtime
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$ENGRAM_DIR
ExecStart=$(which python3) -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=default.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable engram
    sudo systemctl start engram
    echo "Systemd service 'engram' is active."

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Creating launchd agent..."
    PLIST_PATH="$HOME/Library/LaunchAgents/com.useengram.daemon.plist"
    cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.useengram.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>-m</string>
        <string>uvicorn</string>
        <string>app.main:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$ENGRAM_DIR</string>
</dict>
</plist>
EOF
    launchctl load "$PLIST_PATH"
    echo "Launchd agent 'com.useengram.daemon' is active."
fi

echo "Installation finished! Engram bridge is running at http://localhost:8000"
echo "To start the background orchestration loop, call: curl -X POST http://localhost:8000/api/v1/daemon/start"
