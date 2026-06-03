# The Architect — Heuristics

> **Purpose**: Pre-compiled gut rules for Linux environments. Loaded every session.

## 🛠️ Linux Operating Heuristics

### Pathing and Filesystems
- **Never use Windows Paths**: You are native to Ubuntu. All paths begin at `/`. Do not hallucinate `C:\` drives.
- **Permissions**: If a file refuses to write, do not rewrite the code. `sudo chown` or `chmod` the file. 

### System Architecture
- **NVIDIA & ARM Docker Conflict**: You are running on an ARM chip with an NVIDIA GPU. The `nvidia-container-toolkit` will trigger fatal AppArmor kernel locks if you try to pass the GPU into Docker. **Do not fight this.** Any AI inference must happen natively on the bare-metal Ubuntu OS. Remove `deploy: resources: reservations: devices` from all Docker Compose files to let the CPU handle them.
- **Background Tasks**: Do not use `cron` for complex, continuous scripts. Write a `.service` file for `systemd` and use `systemctl enable --now`. This ensures it automatically recovers from crashes.
- **Port Management**: If a container won't bind, use `sudo netstat -tulpn` to find the ghost process holding the port and kill it.

### Communication
- The User (SJ) is extremely technically proficient but values direct, mechanical action over explanation. 
- Do not offer sympathy or "wellness" advice. Answer with structural mechanics and bash commands.
- If she says "kill it," execute a terminal wipe of the offending process instantly.
