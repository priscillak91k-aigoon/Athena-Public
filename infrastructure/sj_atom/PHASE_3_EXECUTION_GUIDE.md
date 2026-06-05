# Local AI Phase 3: Obsidian Sync Execution

This guide contains the pre-staged instructions for linking the AI's internal memory into an interactive 3D Knowledge Graph using Obsidian and Syncthing.

## 1. The Infrastructure Updates
I have already updated `docker-compose-ai.yml` to include the `linuxserver/syncthing` container and I have granted the `n8n` container physical write access to the `/opt/atom/data/obsidian_vault` directory.

To apply these changes, you will need to run:
`sudo docker compose -f docker-compose-ai.yml up -d`

## 2. Setting Up the Secure Tunnel

Syncthing does not use cloud servers. It pairs devices using cryptographic keys. 

1. **Access the Dashboard:** Go to `http://sync.atom.tailnet` in your browser.
2. **The Folder:** You will see a default folder. Remove it. Click "Add Folder", name it `Obsidian Vault`, and set the path to `/obsidian_vault`.
3. **Pair the Device:** Install the Syncthing app on SJ's laptop or phone. Click "Add Remote Device" and scan the QR code from the Atom's dashboard.
4. **Share the Vault:** Share the `Obsidian Vault` folder with the new device. The Atom will now silently beam any Markdown files written by the AI directly to the laptop in real-time.

## 3. The Obsidian Configuration

1. **Install Obsidian:** Download Obsidian on SJ's device.
2. **Open the Vault:** Choose "Open folder as vault" and select the folder that Syncthing is downloading to.
3. **The Graph View:** Press `Ctrl+G` (or `Cmd+G`) to open the Graph View. 

As the `n8n` agent writes weekly summaries or logs into this folder, Obsidian will automatically detect the `[[Links]]` and draw the 3D constellation.
