#!/usr/bin/env python3

import subprocess
import sys
import shutil
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

# ============================================================
# COLORAMA
# ============================================================

try:
    from colorama import Fore, Style, init

    init(autoreset=True)

except ImportError:

    class Dummy:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
        RESET = ""

    Fore = Dummy()
    Style = Dummy()


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

REPORT_DIR = BASE_DIR / "reports"
TARGET_DIR = BASE_DIR / "targets"

# Toolkit-specific environment directory
TOOL_HOME = Path.home() / ".recon-toolkit"

# Go binaries
GO_BIN_DIR = Path.home() / "go" / "bin"

# Waymore virtual environment
WAYMORE_VENV = TOOL_HOME / "waymore-venv"

# SpiderFoot source + virtual environment
SPIDERFOOT_DIR = TOOL_HOME / "spiderfoot"
SPIDERFOOT_VENV = SPIDERFOOT_DIR / ".venv"

# Prevent apt update from running repeatedly
APT_UPDATED = False


# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def banner():

    print(
        Fore.CYAN +
        "=" * 70
    )

    print(
        Fore.CYAN +
        "              PYTHON RECONNAISSANCE TOOLKIT"
    )

    print(
        Fore.CYAN +
        "=" * 70
    )

    print()


def section(title):

    print()

    print(
        Fore.BLUE +
        "=" * 70
    )

    print(
        Fore.BLUE +
        title
    )

    print(
        Fore.BLUE +
        "=" * 70
    )


def success(message):

    print(
        Fore.GREEN +
        "[+] " +
        message
    )


def error(message):

    print(
        Fore.RED +
        "[-] " +
        message
    )


def warning(message):

    print(
        Fore.YELLOW +
        "[!] " +
        message
    )


def info(message):

    print(
        Fore.CYAN +
        "[*] " +
        message
    )


# ============================================================
# INPUT
# ============================================================

def get_input(message):

    try:

        return input(
            Fore.WHITE +
            message
        ).strip()

    except KeyboardInterrupt:

        print()

        error(
            "Operation cancelled."
        )

        sys.exit(0)


# ============================================================
# DIRECTORY CREATION
# ============================================================

def create_directories():

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TARGET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TOOL_HOME.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# FIND COMMAND
# ============================================================

def find_command(command):

    path = shutil.which(command)

    if path:

        return Path(path)

    return None


# ============================================================
# FIND GO TOOL
# ============================================================

def find_go_tool(command):

    tool = GO_BIN_DIR / command

    if (
        tool.exists()
        and os.access(tool, os.X_OK)
    ):

        return tool

    return None


# ============================================================
# SUDO
# ============================================================

def privileged_command(command):

    if os.geteuid() == 0:

        return command

    return ["sudo"] + command


# ============================================================
# APT UPDATE
# ============================================================

def apt_update():

    global APT_UPDATED

    if APT_UPDATED:

        return True

    section(
        "UPDATING APT PACKAGE LIST"
    )

    try:

        command = privileged_command([
            "apt-get",
            "update"
        ])

        result = subprocess.run(command)

        if result.returncode != 0:

            error(
                "apt update failed."
            )

            return False

        APT_UPDATED = True

        success(
            "APT package list updated."
        )

        return True

    except Exception as e:

        error(
            f"APT update error: {e}"
        )

        return False


# ============================================================
# APT INSTALL
# ============================================================

def apt_install(package):

    if not apt_update():

        return False

    section(
        f"INSTALLING {package}"
    )

    try:

        command = privileged_command([
            "apt-get",
            "install",
            "-y",
            package
        ])

        result = subprocess.run(command)

        if result.returncode != 0:

            error(
                f"Failed to install {package}."
            )

            return False

        success(
            f"{package} installed."
        )

        return True

    except Exception as e:

        error(
            f"Installation error: {e}"
        )

        return False


# ============================================================
# GET APT TOOL
# ============================================================

def get_apt_tool(
    command,
    package=None
):

    tool = find_command(command)

    if tool:

        return tool

    warning(
        f"{command} is not installed."
    )

    if package is None:

        package = command

    if not apt_install(package):

        return None

    tool = find_command(command)

    if tool:

        success(
            f"{command} is ready."
        )

        return tool

    error(
        f"{command} could not be found after installation."
    )

    return None


# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

def prepare_python_environment():

    python3 = find_command("python3")

    if not python3:

        warning(
            "python3 is not installed."
        )

        if not apt_install("python3"):

            return False

    # Check venv
    test = subprocess.run(
        [
            "python3",
            "-m",
            "venv",
            "--help"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if test.returncode != 0:

        warning(
            "python3-venv is not installed."
        )

        if not apt_install(
            "python3-venv"
        ):

            return False

    return True


def create_venv(venv_path):

    if venv_path.exists():

        return True

    info(
        f"Creating virtual environment:"
    )

    print(
        Fore.WHITE +
        str(venv_path)
    )

    try:

        result = subprocess.run([
            "python3",
            "-m",
            "venv",
            str(venv_path)
        ])

        if result.returncode != 0:

            error(
                "Failed to create virtual environment."
            )

            return False

        success(
            "Virtual environment created."
        )

        return True

    except Exception as e:

        error(
            f"Venv error: {e}"
        )

        return False


# ============================================================
# GO
# ============================================================

def install_go():

    go = find_command("go")

    if go:

        return go

    warning(
        "Go is not installed."
    )

    if not apt_install(
        "golang-go"
    ):

        return None

    go = find_command("go")

    if go:

        success(
            "Go installed."
        )

        return go

    error(
        "Go installation failed."
    )

    return None


# ============================================================
# INSTALL PROJECTDISCOVERY TOOL
# ============================================================

def get_go_tool(
    command,
    module
):

    tool = find_go_tool(command)

    if tool:

        return tool

    go = install_go()

    if not go:

        return None

    section(
        f"INSTALLING {command}"
    )

    try:

        result = subprocess.run([
            str(go),
            "install",
            "-v",
            module
        ])

        if result.returncode != 0:

            error(
                f"Failed to install {command}."
            )

            return None

        tool = find_go_tool(command)

        if tool:

            success(
                f"{command} installed at {tool}"
            )

            return tool

        error(
            f"{command} was installed but could not be located."
        )

        return None

    except Exception as e:

        error(
            f"Go installation error: {e}"
        )

        return None


# ============================================================
# REPORT FILE
# ============================================================

def get_report_file(
    tool_name,
    target
):

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_target = "".join(
        c
        if c.isalnum() or c in "._-"
        else "_"
        for c in target
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report = REPORT_DIR / (
        f"{tool_name}_"
        f"{safe_target}_"
        f"{timestamp}.txt"
    )

    counter = 1

    while report.exists():

        report = REPORT_DIR / (
            f"{tool_name}_"
            f"{safe_target}_"
            f"{timestamp}_"
            f"{counter}.txt"
        )

        counter += 1

    return report


def write_report_header(
    report,
    tool_name,
    target
):

    with open(
        report,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "=" * 70 +
            "\n"
        )

        f.write(
            f"TOOL   : {tool_name}\n"
        )

        f.write(
            f"TARGET : {target}\n"
        )

        f.write(
            "TIME   : "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        f.write(
            "=" * 70 +
            "\n\n"
        )


# ============================================================
# RUN COMMAND
# ============================================================

def run_command(
    command,
    report=None
):

    print()

    info(
        "Running:"
    )

    print(
        Fore.WHITE +
        " ".join(
            map(str, command)
        )
    )

    print()

    try:

        if report:

            with open(
                report,
                "a",
                encoding="utf-8"
            ) as output:

                result = subprocess.run(
                    [
                        str(x)
                        for x in command
                    ],
                    stdout=output,
                    stderr=subprocess.STDOUT,
                    text=True
                )

        else:

            result = subprocess.run(
                command
            )

        if result.returncode == 0:

            success(
                "Command completed successfully."
            )

        else:

            warning(
                f"Command finished with exit code "
                f"{result.returncode}."
            )

        return result.returncode

    except FileNotFoundError:

        error(
            f"Command not found: {command[0]}"
        )

        return 1

    except KeyboardInterrupt:

        print()

        warning(
            "Command interrupted."
        )

        return 130

    except Exception as e:

        error(
            f"Command execution error: {e}"
        )

        return 1


# ============================================================
# NMAP
# ============================================================

def nmap_recon():

    section(
        "NMAP RECONNAISSANCE"
    )

    nmap = get_apt_tool(
        "nmap"
    )

    if not nmap:

        return

    target = get_input(
        "Enter target IP/domain: "
    )

    if not target:

        error(
            "Target cannot be empty."
        )

        return

    report = get_report_file(
        "nmap",
        target
    )

    write_report_header(
        report,
        "Nmap",
        target
    )

    print(
        "1. Host discovery"
    )

    print(
        "2. Full TCP port scan"
    )

    choice = get_input(
        "Choose option: "
    )

    if choice == "1":

        command = [
            str(nmap),
            "-sn",
            target
        ]

    elif choice == "2":

        command = [
            str(nmap),
            "-p-",
            target
        ]

    else:

        error(
            "Invalid option."
        )

        return

    run_command(
        command,
        report
    )

    success(
        f"Report saved: {report}"
    )


# ============================================================
# DNS
# ============================================================

def dns_recon():

    section(
        "DNS RECONNAISSANCE"
    )

    dig = get_apt_tool(
        "dig",
        "dnsutils"
    )

    if not dig:

        return

    target = get_input(
        "Enter domain: "
    )

    if not target:

        error(
            "Domain cannot be empty."
        )

        return

    report = get_report_file(
        "dns",
        target
    )

    write_report_header(
        report,
        "DNS Recon",
        target
    )

    records = [
        "A",
        "AAAA",
        "NS",
        "MX",
        "SOA",
        "TXT",
        "CNAME"
    ]

    for record in records:

        print(
            Fore.CYAN +
            f"[*] Checking {record}"
        )

        command = [
            str(dig),
            target,
            record
        ]

        run_command(
            command,
            report
        )

    # DMARC
    print(
        Fore.CYAN +
        "[*] Checking DMARC"
    )

    command = [
        str(dig),
        f"_dmarc.{target}",
        "TXT"
    ]

    run_command(
        command,
        report
    )

    # Reverse lookup
    reverse = get_input(
        "Perform reverse DNS lookup? (y/n): "
    ).lower()

    if reverse == "y":

        command = [
            str(dig),
            "-x",
            target
        ]

        run_command(
            command,
            report
        )

    # DNS trace
    trace = get_input(
        "Perform DNS trace? (y/n): "
    ).lower()

    if trace == "y":

        command = [
            str(dig),
            "+trace",
            target
        ]

        run_command(
            command,
            report
        )

    success(
        f"DNS report saved: {report}"
    )


# ============================================================
# HTTPX
# ============================================================

def httpx_recon():

    section(
        "PROJECTDISCOVERY HTTPX"
    )

    info(
        "Using ProjectDiscovery httpx from ~/go/bin."
    )

    info(
        "This avoids the Python HTTPX conflict."
    )

    httpx = get_go_tool(
        "httpx",
        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    )

    if not httpx:

        return

    print(
        "1. Scan a single target"
    )

    print(
        "2. Scan targets from a file"
    )

    choice = get_input(
        "Choose option: "
    )

    if choice == "1":

        target = get_input(
            "Enter URL/domain: "
        )

        if not target:

            error(
                "Target cannot be empty."
            )

            return

        report_target = target

        command = [
            str(httpx),
            "-u",
            target,
            "-title",
            "-status-code",
            "-tech-detect",
            "-web-server",
            "-follow-redirects"
        ]

    elif choice == "2":

        target_file = get_input(
            "Enter the path of the target file: "
        )

        file_path = Path(
            target_file
        ).expanduser()

        if not file_path.is_file():

            error(
                f"Target file does not exist: "
                f"{file_path}"
            )

            return

        report_target = file_path.stem

        command = [
            str(httpx),
            "-l",
            str(file_path),
            "-title",
            "-status-code",
            "-tech-detect",
            "-web-server",
            "-follow-redirects"
        ]

    else:

        error(
            "Invalid option."
        )

        return

    report = get_report_file(
        "httpx",
        report_target
    )

    write_report_header(
        report,
        "ProjectDiscovery HTTPX",
        report_target
    )

    run_command(
        command,
        report
    )

    success(
        f"HTTPX report saved: {report}"
    )


# ============================================================
# WHATWEB
# ============================================================

def whatweb_recon():

    section(
        "WHATWEB RECONNAISSANCE"
    )

    whatweb = get_apt_tool(
        "whatweb"
    )

    if not whatweb:

        return

    target = get_input(
        "Enter URL/domain: "
    )

    if not target:

        error(
            "Target cannot be empty."
        )

        return

    report = get_report_file(
        "whatweb",
        target
    )

    write_report_header(
        report,
        "WhatWeb",
        target
    )

    command = [
        str(whatweb),
        "-a",
        "3",
        target
    ]

    run_command(
        command,
        report
    )

    success(
        f"WhatWeb report saved: {report}"
    )


# ============================================================
# KATANA
# ============================================================

def katana_recon():

    section(
        "KATANA CRAWLER"
    )

    katana = get_go_tool(
        "katana",
        "github.com/projectdiscovery/katana/cmd/katana@latest"
    )

    if not katana:

        return

    print(
        "1. Scan a single target"
    )

    print(
        "2. Scan targets from a file"
    )

    choice = get_input(
        "Choose option: "
    )

    if choice == "1":

        target = get_input(
            "Enter URL: "
        )

        if not target:

            error(
                "Target cannot be empty."
            )

            return

        report_target = target

        command = [
            str(katana),
            "-u",
            target,
            "-d",
            "3"
        ]

    elif choice == "2":

        target_file = get_input(
            "Enter target file path: "
        )

        file_path = Path(
            target_file
        ).expanduser()

        if not file_path.is_file():

            error(
                f"Target file does not exist: "
                f"{file_path}"
            )

            return

        report_target = file_path.stem

        command = [
            str(katana),
            "-list",
            str(file_path),
            "-d",
            "3"
        ]

    else:

        error(
            "Invalid option."
        )

        return

    report = get_report_file(
        "katana",
        report_target
    )

    write_report_header(
        report,
        "Katana",
        report_target
    )

    run_command(
        command,
        report
    )

    success(
        f"Katana report saved: {report}"
    )


# ============================================================
# FFUF
# ============================================================

def ffuf_recon():

    section(
        "FFUF FUZZING"
    )

    ffuf = get_go_tool(
        "ffuf",
        "github.com/ffuf/ffuf/v2@latest"
    )

    if not ffuf:

        return

    target = get_input(
        "Enter target URL containing FUZZ: "
    )

    if not target:

        error(
            "Target cannot be empty."
        )

        return

    if "FUZZ" not in target:

        warning(
            "URL does not contain FUZZ."
        )

        target += "/FUZZ"

    wordlist = get_input(
        "Enter wordlist path: "
    )

    wordlist_path = Path(
        wordlist
    ).expanduser()

    if not wordlist_path.is_file():

        error(
            f"Wordlist does not exist: "
            f"{wordlist_path}"
        )

        return

    report = get_report_file(
        "ffuf",
        "fuzz"
    )

    json_report = report.with_suffix(
        ".json"
    )

    write_report_header(
        report,
        "FFUF",
        target
    )

    command = [
        str(ffuf),
        "-w",
        str(wordlist_path),
        "-u",
        target,
        "-of",
        "json",
        "-o",
        str(json_report)
    ]

    run_command(
        command,
        report
    )

    success(
        f"FFUF text report saved: {report}"
    )

    success(
        f"FFUF JSON report saved: {json_report}"
    )


# ============================================================
# AMASS
# ============================================================

def amass_recon():

    section(
        "AMASS PASSIVE ENUMERATION"
    )

    amass = get_apt_tool(
        "amass"
    )

    if not amass:

        return

    target = get_input(
        "Enter domain: "
    )

    if not target:

        error(
            "Domain cannot be empty."
        )

        return

    report = get_report_file(
        "amass",
        target
    )

    write_report_header(
        report,
        "Amass Passive Enumeration",
        target
    )

    command = [
        str(amass),
        "enum",
        "-passive",
        "-src",
        "-d",
        target
    ]

    run_command(
        command,
        report
    )

    success(
        f"Amass report saved: {report}"
    )


# ============================================================
# WAYMORE INSTALLATION
# ============================================================

def install_waymore():

    if not prepare_python_environment():

        return None

    if not create_venv(
        WAYMORE_VENV
    ):

        return None

    venv_python = (
        WAYMORE_VENV /
        "bin" /
        "python"
    )

    if not venv_python.exists():

        error(
            "Waymore Python executable not found."
        )

        return None

    check = subprocess.run(
        [
            str(venv_python),
            "-m",
            "pip",
            "show",
            "waymore"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if check.returncode != 0:

        section(
            "INSTALLING WAYMORE"
        )

        result = subprocess.run([
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip"
        ])

        if result.returncode != 0:

            error(
                "Failed to upgrade pip."
            )

            return None

        result = subprocess.run([
            str(venv_python),
            "-m",
            "pip",
            "install",
            "waymore"
        ])

        if result.returncode != 0:

            error(
                "Failed to install Waymore."
            )

            return None

    success(
        "Waymore is ready."
    )

    return venv_python


# ============================================================
# WAYMORE RECON
# ============================================================

def waymore_recon():

    section(
        "HISTORICAL URL DISCOVERY"
    )

    python = install_waymore()

    if not python:

        return

    target = get_input(
        "Enter domain: "
    )

    if not target:

        error(
            "Domain cannot be empty."
        )

        return

    report = get_report_file(
        "waymore",
        target
    )

    write_report_header(
        report,
        "Waymore",
        target
    )

    command = [
        str(python),
        "-m",
        "waymore",
        "-i",
        target,
        "-mode",
        "U"
    ]

    run_command(
        command,
        report
    )

    success(
        "Waymore completed."
    )

    warning(
        "URLScan/VirusTotal API-key messages are optional "
        "and can be ignored."
    )

    success(
        f"Waymore report saved: {report}"
    )


# ============================================================
# SPIDERFOOT INSTALLATION
# ============================================================

def install_spiderfoot():

    section(
        "SPIDERFOOT INSTALLATION"
    )

    if not prepare_python_environment():

        return None, None

    sf_file = (
        SPIDERFOOT_DIR /
        "sf.py"
    )

    # --------------------------------------------------------
    # Git
    # --------------------------------------------------------

    git = find_command(
        "git"
    )

    if not git:

        warning(
            "Git is not installed."
        )

        if not apt_install(
            "git"
        ):

            return None, None

        git = find_command(
            "git"
        )

        if not git:

            error(
                "Git installation failed."
            )

            return None, None

    # --------------------------------------------------------
    # SpiderFoot dependencies
    # --------------------------------------------------------

    dependencies = [
        "python3",
        "python3-dev",
        "python3-venv",
        "build-essential",
        "libxml2-dev",
        "libxslt1-dev",
        "zlib1g-dev"
    ]

    for package in dependencies:

        check = subprocess.run(
            [
                "dpkg",
                "-s",
                package
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if check.returncode != 0:

            if not apt_install(
                package
            ):

                warning(
                    f"Could not install dependency: "
                    f"{package}"
                )

    # --------------------------------------------------------
    # Clone SpiderFoot
    # --------------------------------------------------------

    if not sf_file.exists():

        if SPIDERFOOT_DIR.exists():

            warning(
                "SpiderFoot directory exists but sf.py "
                "was not found."
            )

            shutil.rmtree(
                SPIDERFOOT_DIR,
                ignore_errors=True
            )

        section(
            "CLONING SPIDERFOOT"
        )

        result = subprocess.run([
            str(git),
            "clone",
            "https://github.com/smicallef/spiderfoot.git",
            str(SPIDERFOOT_DIR)
        ])

        if result.returncode != 0:

            error(
                "Failed to clone SpiderFoot."
            )

            return None, None

    else:

        success(
            f"SpiderFoot source found at "
            f"{SPIDERFOOT_DIR}"
        )

    if not sf_file.exists():

        error(
            "SpiderFoot sf.py was not found."
        )

        return None, None

    # --------------------------------------------------------
    # Create SpiderFoot venv
    # --------------------------------------------------------

    if not create_venv(
        SPIDERFOOT_VENV
    ):

        return None, None

    venv_python = (
        SPIDERFOOT_VENV /
        "bin" /
        "python"
    )

    if not venv_python.exists():

        error(
            "SpiderFoot Python executable not found."
        )

        return None, None

    # --------------------------------------------------------
    # Upgrade pip
    # --------------------------------------------------------

    section(
        "PREPARING SPIDERFOOT ENVIRONMENT"
    )

    result = subprocess.run([
        str(venv_python),
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
        "setuptools",
        "wheel"
    ])

    if result.returncode != 0:

        error(
            "Failed to upgrade SpiderFoot pip tools."
        )

        return None, None

    # --------------------------------------------------------
    # Requirements
    # --------------------------------------------------------

    requirements = (
        SPIDERFOOT_DIR /
        "requirements.txt"
    )

    if requirements.exists():

        info(
            "Installing SpiderFoot requirements..."
        )

        result = subprocess.run([
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            str(requirements)
        ])

        if result.returncode != 0:

            warning(
                "Some SpiderFoot requirements failed."
            )

    # --------------------------------------------------------
    # CherryPy fix
    # --------------------------------------------------------

    info(
        "Installing SpiderFoot runtime dependency: cherrypy"
    )

    result = subprocess.run([
        str(venv_python),
        "-m",
        "pip",
        "install",
        "cherrypy"
    ])

    if result.returncode != 0:

        error(
            "Failed to install CherryPy."
        )

        return None, None

    # --------------------------------------------------------
    # Verify SpiderFoot
    # --------------------------------------------------------

    section(
        "VERIFYING SPIDERFOOT"
    )

    try:

        result = subprocess.run(
            [
                str(venv_python),
                str(sf_file),
                "-h"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60
        )

        if result.returncode != 0:

            error(
                "SpiderFoot verification failed."
            )

            print(
                Fore.YELLOW +
                result.stdout[-3000:]
            )

            return None, None

        success(
            "SpiderFoot installation verified."
        )

    except subprocess.TimeoutExpired:

        error(
            "SpiderFoot verification timed out."
        )

        return None, None

    except Exception as e:

        error(
            f"SpiderFoot verification error: {e}"
        )

        return None, None

    return (
        venv_python,
        sf_file
    )


# ============================================================
# SPIDERFOOT RECON
# ============================================================

def spiderfoot_recon():

    section(
        "SPIDERFOOT OSINT"
    )

    venv_python, sf_file = (
        install_spiderfoot()
    )

    if not venv_python or not sf_file:

        return

    target = get_input(
        "Enter domain/IP: "
    )

    if not target:

        error(
            "Target cannot be empty."
        )

        return

    report = get_report_file(
        "spiderfoot",
        target
    )

    write_report_header(
        report,
        "SpiderFoot",
        target
    )

    command = [
        str(venv_python),
        str(sf_file),
        "-s",
        target,
        "-u",
        "passive",
        "-o",
        "tab"
    ]

    run_command(
        command,
        report
    )

    success(
        f"SpiderFoot report saved: {report}"
    )


# ============================================================
# CRT.SH
# ============================================================

def crtsh_recon():

    section(
        "CERTIFICATE TRANSPARENCY / CRT.SH"
    )

    target = get_input(
        "Enter domain: "
    )

    if not target:

        error(
            "Domain cannot be empty."
        )

        return

    target = (
        target
        .replace("https://", "")
        .replace("http://", "")
        .split("/")[0]
    )

    report = get_report_file(
        "crtsh",
        target
    )

    write_report_header(
        report,
        "crt.sh Certificate Transparency",
        target
    )

    encoded_domain = urllib.parse.quote(
        f"%.{target}"
    )

    url = (
        "https://crt.sh/"
        f"?q={encoded_domain}"
        "&output=json"
    )

    info(
        "Querying crt.sh..."
    )

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0 ReconToolkit"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            data = response.read()

        results = json.loads(
            data.decode("utf-8")
        )

    except Exception as e:

        error(
            f"crt.sh request failed: {e}"
        )

        return

    if not results:

        warning(
            "No certificate records returned."
        )

        return

    # --------------------------------------------------------
    # Extract DNS names
    # --------------------------------------------------------

    dns_names = set()

    for certificate in results:

        names = certificate.get(
            "name_value",
            ""
        )

        for name in names.splitlines():

            name = name.strip().lower()

            if name.startswith("*."):

                name = name[2:]

            if name:

                dns_names.add(
                    name
                )

    # --------------------------------------------------------
    # Save certificate information
    # --------------------------------------------------------

    with open(
        report,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            "\nCERTIFICATE RECORDS\n"
        )

        f.write(
            "=" * 70 +
            "\n"
        )

        for certificate in results:

            cert_id = certificate.get(
                "id",
                "N/A"
            )

            issuer = certificate.get(
                "issuer_name",
                "N/A"
            )

            common_name = certificate.get(
                "common_name",
                "N/A"
            )

            not_before = certificate.get(
                "not_before",
                "N/A"
            )

            not_after = certificate.get(
                "not_after",
                "N/A"
            )

            f.write(
                f"Certificate ID : {cert_id}\n"
            )

            f.write(
                f"Issuer        : {issuer}\n"
            )

            f.write(
                f"Common Name   : {common_name}\n"
            )

            f.write(
                f"Valid From    : {not_before}\n"
            )

            f.write(
                f"Valid Until   : {not_after}\n"
            )

            f.write(
                "DNS Names     :\n"
            )

            names = certificate.get(
                "name_value",
                ""
            )

            for name in names.splitlines():

                f.write(
                    f"  {name}\n"
                )

            f.write(
                "-" * 70 +
                "\n"
            )

        f.write(
            "\nUNIQUE DNS NAMES / SUBDOMAINS\n"
        )

        f.write(
            "=" * 70 +
            "\n"
        )

        for name in sorted(
            dns_names
        ):

            f.write(
                name +
                "\n"
            )

    success(
        f"Found {len(results)} certificate records."
    )

    success(
        f"Found {len(dns_names)} unique DNS names."
    )

    success(
        f"crt.sh report saved: {report}"
    )


# ============================================================
# CLEANUP PYTHON ENVIRONMENTS
# ============================================================

def cleanup_environments():

    section(
        "DELETE PYTHON ENVIRONMENTS"
    )

    print(
        Fore.YELLOW +
        "This will delete ONLY the environments/source "
        "downloaded by this toolkit."
    )

    print()

    print(
        f"1. Waymore environment:"
    )

    print(
        Fore.WHITE +
        f"   {WAYMORE_VENV}"
    )

    print()

    print(
        f"2. SpiderFoot environment/source:"
    )

    print(
        Fore.WHITE +
        f"   {SPIDERFOOT_DIR}"
    )

    print()

    warning(
        "Installed system tools will NOT be removed."
    )

    warning(
        "Go tools such as httpx, katana and ffuf "
        "will NOT be removed."
    )

    print()

    confirm = get_input(
        "Type DELETE to continue: "
    )

    if confirm != "DELETE":

        warning(
            "Cleanup cancelled."
        )

        return

    print()

    # --------------------------------------------------------
    # Waymore
    # --------------------------------------------------------

    if WAYMORE_VENV.exists():

        try:

            shutil.rmtree(
                WAYMORE_VENV
            )

            success(
                f"Deleted Waymore environment: "
                f"{WAYMORE_VENV}"
            )

        except Exception as e:

            error(
                f"Failed to delete Waymore environment: "
                f"{e}"
            )

    else:

        info(
            "Waymore environment does not exist."
        )

    # --------------------------------------------------------
    # SpiderFoot
    # --------------------------------------------------------

    if SPIDERFOOT_DIR.exists():

        try:

            shutil.rmtree(
                SPIDERFOOT_DIR
            )

            success(
                f"Deleted SpiderFoot source/environment: "
                f"{SPIDERFOOT_DIR}"
            )

        except Exception as e:

            error(
                f"Failed to delete SpiderFoot directory: "
                f"{e}"
            )

    else:

        info(
            "SpiderFoot environment does not exist."
        )

    # --------------------------------------------------------
    # Remove empty TOOL_HOME
    # --------------------------------------------------------

    if TOOL_HOME.exists():

        try:

            TOOL_HOME.rmdir()

            success(
                f"Removed empty directory: "
                f"{TOOL_HOME}"
            )

        except OSError:

            # Directory is not empty.
            pass

    print()

    success(
        "Python environment cleanup completed."
    )

    print()

    info(
        "System tools were not removed."
    )


# ============================================================
# PASSIVE MENU
# ============================================================

def passive_menu():

    while True:

        section(
            "PASSIVE RECONNAISSANCE"
        )

        print(
            "1. Amass"
        )

        print(
            "2. crt.sh"
        )

        print(
            "3. Waymore"
        )

        print(
            "4. SpiderFoot"
        )

        print(
            "5. Back"
        )

        print()

        choice = get_input(
            "Choose option: "
        )

        if choice == "1":

            amass_recon()

        elif choice == "2":

            crtsh_recon()

        elif choice == "3":

            waymore_recon()

        elif choice == "4":

            spiderfoot_recon()

        elif choice == "5":

            break

        else:

            error(
                "Invalid option."
            )


# ============================================================
# ACTIVE MENU
# ============================================================

def active_menu():

    while True:

        section(
            "ACTIVE RECONNAISSANCE"
        )

        print(
            "1. Nmap"
        )

        print(
            "2. DNS / Dig"
        )

        print(
            "3. HTTPX"
        )

        print(
            "4. WhatWeb"
        )

        print(
            "5. Katana"
        )

        print(
            "6. FFUF"
        )

        print(
            "7. Back"
        )

        print()

        choice = get_input(
            "Choose option: "
        )

        if choice == "1":

            nmap_recon()

        elif choice == "2":

            dns_recon()

        elif choice == "3":

            httpx_recon()

        elif choice == "4":

            whatweb_recon()

        elif choice == "5":

            katana_recon()

        elif choice == "6":

            ffuf_recon()

        elif choice == "7":

            break

        else:

            error(
                "Invalid option."
            )


# ============================================================
# MAIN MENU
# ============================================================

def main():

    create_directories()

    while True:

        banner()

        print(
            Fore.GREEN +
            "1. Passive Reconnaissance"
        )

        print(
            Fore.RED +
            "2. Active Reconnaissance"
        )

        print(
            Fore.YELLOW +
            "3. Delete Python Environments"
        )

        print(
            Fore.CYAN +
            "4. Exit"
        )

        print()

        choice = get_input(
            "Choose option: "
        )

        if choice == "1":

            passive_menu()

        elif choice == "2":

            active_menu()

        elif choice == "3":

            cleanup_environments()

        elif choice == "4":

            print()

            success(
                "Reconnaissance Toolkit closed."
            )

            break

        else:

            error(
                "Invalid option. "
                "Choose 1, 2, 3 or 4."
            )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()

        warning(
            "Program interrupted by user."
        )

    except Exception as e:

        print()

        error(
            f"Unexpected error: {e}"
        )