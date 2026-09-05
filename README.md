# 🔎 Reconnaissance Toolkit

A Python-based reconnaissance toolkit that automates passive and active reconnaissance by integrating multiple cybersecurity tools into a single command-line interface.

## ✨ Features

- Passive reconnaissance
- Active reconnaissance
- Automatic detection of required tools
- Automatic installation of supported dependencies
- Automatic Python virtual environment creation
- Target file support
- Timestamped reports
- DNS reconnaissance
- Port scanning
- HTTP/HTTPS probing
- Web technology detection
- Web crawling
- Content discovery
- Subdomain enumeration
- Certificate Transparency enumeration
- Historical URL discovery
- OSINT reconnaissance
- Python environment cleanup

## 🛠️ Tools Used

### 🔵 Passive Reconnaissance

| Tool | Purpose |
|---|---|
| Amass | Passive subdomain enumeration |
| crt.sh | Certificate Transparency and subdomain discovery |
| Waymore | Historical URL discovery |
| SpiderFoot | Automated OSINT reconnaissance |

### 🔴 Active Reconnaissance

| Tool | Purpose |
|---|---|
| Nmap | Host discovery and port scanning |
| dig | DNS reconnaissance |
| HTTPX | HTTP/HTTPS service probing |
| WhatWeb | Web technology identification |
| Katana | Web crawling and endpoint discovery |
| FFUF | Web content discovery |

## 📋 Requirements

- Python 3
- Git
- Go
- Internet connection
- Kali Linux or Debian-based Linux
- `apt` package manager

Some dependencies and tools can be installed automatically by the toolkit.

## ⚙️ Installation

Clone the repository:

    git clone https://github.com/nkharsha2006/reconnaissance.git

Move into the project directory:

    cd reconnaissance

Run the toolkit:

    python3 Reconnaissance.py

## 🚀 Usage

After starting the program, the main menu provides:

    1. Passive Reconnaissance
    2. Active Reconnaissance
    3. Delete Python Environments
    4. Exit

### 🔵 Passive Reconnaissance

The passive reconnaissance menu includes:

    Amass
    crt.sh
    Waymore
    SpiderFoot

### 🔴 Active Reconnaissance

The active reconnaissance menu includes:

    Nmap
    DNS / dig
    HTTPX
    WhatWeb
    Katana
    FFUF

## 📄 Reports

The toolkit automatically saves command output into timestamped report files.

Reports are stored in:

    reports/

Example:

    reports/
    ├── nmap_*.txt
    ├── dns_*.txt
    ├── httpx_*.txt
    ├── whatweb_*.txt
    ├── katana_*.txt
    ├── ffuf_*.txt
    ├── amass_*.txt
    ├── waymore_*.txt
    ├── spiderfoot_*.txt
    └── crtsh_*.txt

Both standard output and error output are captured in the reports.

## 📁 Project Structure

    reconnaissance/
    │
    ├── Reconnaissance.py
    ├── README.md
    ├── .gitignore
    │
    ├── reports/
    └── targets/

The toolkit also uses:

    ~/.recon-toolkit/

for tool-specific environments and installations.

## 🐍 Python Environments

The toolkit creates separate environments for tools that require isolated Python dependencies.

### Waymore

    ~/.recon-toolkit/waymore-venv/

### SpiderFoot

    ~/.recon-toolkit/spiderfoot/
    └── .venv/

This helps prevent dependency conflicts between different tools.

## 🧹 Environment Cleanup

The toolkit provides an environment cleanup option:

    3. Delete Python Environments

This removes toolkit-managed Python environments and the SpiderFoot installation.

It does not remove:

- System-installed tools
- Go binaries
- Reports
- Target files

The cleanup operation requires confirmation before deletion.

## 🔍 Reconnaissance Workflow

The toolkit can be used as a basic reconnaissance workflow:

    Target
      │
      ├── Passive Reconnaissance
      │     ├── Amass
      │     ├── crt.sh
      │     ├── Waymore
      │     └── SpiderFoot
      │
      └── Active Reconnaissance
            ├── Nmap
            ├── DNS / dig
            ├── HTTPX
            ├── WhatWeb
            ├── Katana
            └── FFUF
                  │
                  ↓
               Reports

## 🔐 Security & Authorization

This toolkit is intended for:

- Cybersecurity education
- CTF environments
- Security research
- Authorized penetration testing
- Systems and applications owned by the tester

Active reconnaissance generates traffic toward target systems. Always obtain explicit permission before testing systems, networks, domains, or applications that you do not own.

## 🚧 Future Improvements

- [ ] Command-line argument support
- [ ] Improved error handling
- [ ] Advanced logging
- [ ] HTML report generation
- [ ] JSON report generation
- [ ] Centralized configuration
- [ ] Parallel tool execution
- [ ] Additional reconnaissance tools
- [ ] Automated testing
- [ ] Improved report visualization

## 👨‍💻 Author

**Harsha Vardhan Reddy**

GitHub:
https://github.com/nkharsha2006

## ⚠️ Disclaimer

This project is developed for educational and authorized security-testing purposes only.

Do not use this toolkit against systems, networks, domains, or applications without proper authorization.

The author is not responsible for any misuse, damage, or illegal activity involving this project.
