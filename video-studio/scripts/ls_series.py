#!/usr/bin/env python3
"""ls_series.py - plan a complete Linux beginner-to-advanced Instagram Reels series.

Generates:
  series/series_plan.md        — 30-day schedule (1 main + 1 tip Reel per day)
  series/episode_NNN/          — per-episode script.md + slides_spec.json
                                  (ready for vs_slides / vs_plan / vs_render)

Usage:
  ls_series.py --out series/ [--episode N]   # N = only scaffold one episode
Exit: 0 ok.
"""
import argparse
import json
import sys
from pathlib import Path

# day -> (phase, main{title, hook, keywords, points}, tip{title, hook, cmd, note})
CURRICULUM = [
    ("Beginner Basics",
     {"title": "Linux Kya Hai", "hook": "Linux wo system hai jiske andar aap sab kuch control karte hain — aaj isko samajhte hain.",
      "keywords": ["Linux", "Open Source", "Terminal"],
      "points": ["Linux ek free, open-source operating system hai",
                 "Aap usme bina darr ke saari files manage kar sakte hain",
                 "Terminal hi aapka sabse powerful tool hai"]},
     {"title": "Command: ls", "hook": "Pehla command: ls — folder ke andar kya hai, yeh batata hai.",
      "cmd": "ls -la", "note": "-la sab files dikhata hai, including hidden ones"}),
    ("Beginner Basics",
     {"title": "Terminal Pe Pehla Baar", "hook": "Terminal ko kholna aur idhar-udhar chalna — 5 second mein sikhaate hain.",
      "keywords": ["Terminal", "Navigation", "Commands"],
      "points": ["pwd: aap kahan khade ho, yeh batata hai",
                 "cd: ek folder se doosre folder mein jaate hain",
                 "ls: folder ke andar kya hai, dekhte hain"]},
     {"title": "Command: cd", "hook": "Folder change karna — ek command, zero confusion.",
      "cmd": "cd ~/Documents", "note": "~ aapka home folder hota hai"}),
    ("Beginner Basics",
     {"title": "Files Aur Directories", "hook": "Files banana, folder banana, delete karna — basics aaj khatam.",
      "keywords": ["Files", "Directories", "Manage"],
      "points": ["mkdir: naya folder banate hain",
                 "touch: nayi file khali banate hain",
                 "rm: files delete karte hain — careful, no undo"]},
     {"title": "Command: mkdir", "hook": "Naya folder 2 second mein — mkdir.",
      "cmd": "mkdir my-folder", "note": "Name mein spaces nahi hone chahiye"}),
    ("Beginner Basics",
     {"title": "Permissions Ek Bar Samajh Lo", "hook": "Har file pe teen groups aur teen rights — aaj ek baar samajh lo, phir kabhi confusion nahi hogi.",
      "keywords": ["Permissions", "rwx", "chmod"],
      "points": ["3 groups: owner, group, others",
                 "3 rights: read (r), write (w), execute (x)",
                 "chmod 755 directory, chmod 644 file — yaad rakhiye"]},
     {"title": "Command: chmod", "hook": "chmod se permissions change karte hain — ek number se poora control.",
      "cmd": "chmod 755 file.sh", "note": "7 = rwx, 5 = r-x"}),
    ("Beginner Basics",
     {"title": "Files Padhna", "hook": "File ke andar kya hai — cat, head aur tail se dekhte hain.",
      "keywords": ["cat", "head", "tail"],
      "points": ["cat: poori file ek saath print karta hai",
                 "head: sirf first 10 lines dikhata hai",
                 "tail: last lines dikhata hai, logs ke liye perfect"]},
     {"title": "Command: tail", "hook": "Log files ke aakhri lines — tail -f live dekhte hain.",
      "cmd": "tail -f app.log", "note": "-f live follow karta hai, Ctrl+C rukne ke liye"}),
    ("Beginner Basics",
     {"title": "Help Aur Docs", "hook": "Koi command bhul gaya? Aap khud hi dhundh sakte hain — help aur man.",
      "keywords": ["help", "man", "Docs"],
      "points": ["--help: kisi command ki basic help dikhata hai",
                 "man command: detailed manual, pura reference",
                 "Commands yaad rakhne ki jarurat nahi — docs aapka dost hain"]},
     {"title": "Command: man", "hook": "Har command ka pura book — man.",
      "cmd": "man ls", "note": "q se exit, / se search within manual"}),
    ("Core Commands",
     {"title": "Search Karo  Smartly", "hook": "Bada folder, chhota target — grep aur find aaj aapka dost hain.",
      "keywords": ["grep", "find", "Search"],
      "points": ["grep: text search karta hai files ke andar",
                 "find: files find karta hai naam, size ya time ke hisaab se",
                 "-i: case-insensitive search"]},
     {"title": "Command: find", "hook": "Koi bhi file khojna — find se easy nahi ho sakta.",
      "cmd": "find . -name '*.txt'", "note": ". current folder mein search karta hai"}),
    ("Core Commands",
     {"title": "Pipes Aur Redirection", "hook": "Ek command ka output doosre command mein daalna — pipes ka magic.",
      "keywords": ["Pipes", "Redirection", "Magic"],
      "points": ["| (pipe): ek command ka output doosre command ko deta hai",
                 ">: output ko file mein save karta hai",
                 ">>: file ke andar append karta hai, file khatam nahi hota"]},
     {"title": "Command: grep | wc", "hook": "Kai lines match hain — counting ek pipe mein.",
      "cmd": "grep -c error app.log", "note": "-c sirf count print karta hai"}),
    ("Core Commands",
     {"title": "Processes Ko Samajhna", "hook": "Aapke system pe kya chal raha hai — ps aur top batate hain.",
      "keywords": ["Processes", "ps", "top"],
      "points": ["ps: chal rahe processes ki list dikhata hai",
                 "top: live process monitor, CPU/memory usage ke saath",
                 "kill: ek process khatam karta hai"]},
     {"title": "Command: top", "hook": "System ka heartbeat — top.",
      "cmd": "top", "note": "q se exit, 1 se CPU per core dikhaye"}),
    ("Core Commands",
     {"title": "Vim Shuru Karo", "hook": "Linux ka sabse famous editor vim — aaj pehli baar kholte hain.",
      "keywords": ["vim", "Editor", "Terminal"],
      "points": ["vi file.txt: file kholte hain vim mein",
                 "i: insert mode, text likhne ke liye",
                 "Esc aur :wq: file save karke exit"]},
     {"title": "Command: vim", "hook": "Vim mein file save karna — :wq yaad rakhiye.",
      "cmd": ":wq", "note": "w = write, q = quit"}),
    ("Core Commands",
     {"title": "Permissions Ka Deep Dive", "hook": "chmod, chown, umask — permissions ka poora control aaj aapke haath.",
      "keywords": ["chmod", "chown", "umask"],
      "points": ["chown: file ka owner change karta hai",
                 "umask: nayi files ka default permission set karta hai",
                 "755, 644, 600 — teen numbers sabse common hain"]},
     {"title": "Command: umask", "hook": "Nayi files ke default permissions — umask se set karo.",
      "cmd": "umask 022", "note": "022 se group/others ke liye write blocked"}),
    ("Core Commands",
     {"title": "Copy, Move, Compare", "hook": "Files ko move, copy, compare — cp, mv, diff ka khaas maja.",
      "keywords": ["cp", "mv", "diff"],
      "points": ["cp: file ya folder copy karta hai",
                 "mv: file move ya rename karta hai",
                 "diff: do files mein kya different hai, batata hai"]},
     {"title": "Command: diff", "hook": "Do files mein difference — diff se instant pata.",
      "cmd": "diff file1.txt file2.txt", "note": "< aur > se difference dikhata hai"}),
    ("Shell & Scripting",
     {"title": "Bash Ki Shuruaat", "hook": "Bash — aapka personal scripting language. Aaj variables aur echo se start karte hain.",
      "keywords": ["Bash", "Variables", "echo"],
      "points": ["echo: text print karta hai terminal pe",
                 "variables: k = value, $k se use karte hain",
                 "bash script.sh: script run karte hain"]},
     {"title": "Command: echo", "hook": "Terminal pe kuch print karna — echo.",
      "cmd": "echo Hello Linux", "note": "Semicolon se ek line mein multiple commands"}),
    ("Shell & Scripting",
     {"title": "Conditionals IF Else", "hook": "Script mein decision lena — if/else se shakti aapke haath.",
      "keywords": ["if", "else", "Logic"],
      "points": ["if [ condition ]; then ... fi",
                 "else block dusre case ke liye",
                 "-f file check, -d folder check — common conditions"]},
     {"title": "Command: test -f", "hook": "File exist karta hai ya nahi — test se check.",
      "cmd": "[ -f file.txt ] && echo yes", "note": "&& = only if true, run next"}),
    ("Shell & Scripting",
     {"title": "Loops For Aur While", "hook": "Kai baar wahi kaam repeat karna — loops aaj aapka time bachayenge.",
      "keywords": ["for", "while", "Loops"],
      "points": ["for: list ya range pe iterate karta hai",
                 "while: condition true hai tak chalta hai",
                 "Loops se bulk tasks ek shot mein ho jaate hain"]},
     {"title": "Command: for", "hook": "Har file pe loop — for loop ka sabse common use.",
      "cmd": "for f in *.txt; do echo $f; done", "note": "* glob sab txt files dikhata hai"}),
    ("Shell & Scripting",
     {"title": "Functions Aur Scripts", "hook": "Reusable code banate hain — functions aur aapka pehla real script.",
      "keywords": ["Functions", "Scripts", "Reusable"],
      "points": ["function naam() { ... }: reusable block",
                 "#!/bin/bash: script ka pehla line, interpreter batata hai",
                 "chmod +x aur ./script.sh: run karna"]},
     {"title": "Command: chmod +x", "hook": "Script ko executable banana — chmod +x.",
      "cmd": "chmod +x myscript.sh", "note": "Phir ./myscript.sh se directly run"}),
    ("Shell & Scripting",
     {"title": "Regex Ki Duniya", "hook": "Text matching ka sabse powerful tool — regex, aaj basics pe padhate hain.",
      "keywords": ["Regex", "Matching", "Patterns"],
      "points": [". kisi bhi ek character se match karta hai",
                 "* zero ya zyada repetition dikhata hai",
                 "grep -E regex ke liye extended mode"]},
     {"title": "Command: grep -E", "hook": "Regex se search — grep -E.",
      "cmd": "grep -E 'log[0-9]+' app.log", "note": "[0-9] = digit, + = at least one"}),
    ("Shell & Scripting",
     {"title": "Aapka Pehla Script", "hook": "Aaj ek real script banate hain — backup reminder, end to end.",
      "keywords": ["Script", "Backup", "Project"],
      "points": ["Shebang + variables + loop + conditional",
                 "Script file banake chmod +x karein",
                 "Small script se automation ka pehla kadam"]},
     {"title": "Command: crontab", "hook": "Script ko roz automatically chalne dijiye — cron.",
      "cmd": "crontab -e", "note": "0 9 * * * = roz 9 AM chale"}),
    ("System Administration",
     {"title": "Users Aur Groups", "hook": "System pe aapke jaise logs — users aur groups, aaj manage karte hain.",
      "keywords": ["Users", "Groups", "sudo"],
      "points": ["useradd: naya user banate hain",
                 "groupadd: groups banate hain",
                 "sudo: admin powers temporary tau leta hai"]},
     {"title": "Command: sudo", "hook": "Admin powers — sudo ka sahi istemal.",
      "cmd": "sudo apt update", "note": "Only when needed — extra powers, extra responsibility"}),
    ("System Administration",
     {"title": "Packages Install Karo", "hook": "Software install karna — apt aur dnf, ek command mein.",
      "keywords": ["apt", "dnf", "Packages"],
      "points": ["apt (Debian/Ubuntu) aur dnf (RHEL/Fedora)",
                 "apt update + apt install package-name",
                 "apt remove: software hatate hain"]},
     {"title": "Command: apt", "hook": "Package search aur install — apt.",
      "cmd": "apt search python3", "note": "Phir apt install python3"}),
    ("System Administration",
     {"title": "Services Aur systemd", "hook": "System ke services kaise chalte hain — systemd aaj samjhte hain.",
      "keywords": ["systemd", "Services", "systemctl"],
      "points": ["systemctl status: service chal raha hai kya",
                 "systemctl start/stop/restart: control",
                 "systemctl enable: boot pe auto-start"]},
     {"title": "Command: systemctl", "hook": "Service check — systemctl status.",
      "cmd": "systemctl status nginx", "note": "Active ya inactive dikhata hai"}),
    ("System Administration",
     {"title": "Networking Basics", "hook": "Network ki duniya — ip, ping, curl se pehli jaankari.",
      "keywords": ["Network", "ip", "curl"],
      "points": ["ip addr: aapka IP address dikhata hai",
                 "ping: kisi host tak pahuncha test karta hai",
                 "curl: web content fetch karta hai terminal se"]},
     {"title": "Command: curl", "hook": "Terminal se web fetch — curl.",
      "cmd": "curl https://example.com", "note": "-I header only, -o file save"}),
    ("System Administration",
     {"title": "Disks Aur Filesystems", "hook": "Disk space ka track karna — df, du aur mount.",
      "keywords": ["Disks", "df", "du"],
      "points": ["df -h: disk space bacha hua dikhata hai",
                 "du -sh: folder ka size dikhata hai",
                 "mount: external drives connect karte hain"]},
     {"title": "Command: du", "hook": "Bada folder ka size — du -sh.",
      "cmd": "du -sh /var/log", "note": "-s summary, -h human readable"}),
    ("System Administration",
     {"title": "Logs Ko Read Karo", "hook": "System kya keh raha hai — logs aaj aapki guidance hain.",
      "keywords": ["Logs", "journalctl", "dmesg"],
      "points": ["journalctl: systemd logs dekhte hain",
                 "journalctl -u service: ek service ke liye",
                 "dmesg: kernel logs, boot ke time ke"]},
     {"title": "Command: journalctl", "hook": "Last 100 lines of system log — journalctl.",
      "cmd": "journalctl -n 100", "note": "-f follow live, -u service filter"}),
    ("Advanced",
     {"title": "sed Aur awk", "hook": "Text processing ka heavy artillery — sed aur awk, aaj basics.",
      "keywords": ["sed", "awk", "Text Processing"],
      "points": ["sed: find and replace, line editing karta hai",
                 "awk: columns aur patterns se data process karta hai",
                 "Inse big text tasks ek shot mein ho jaate hain"]},
     {"title": "Command: sed", "hook": "File mein replace karna — sed.",
      "cmd": "sed 's/old/new/' file.txt", "note": "-i se file itself change karo"}),
    ("Advanced",
     {"title": "Cron Aur Scheduling", "hook": "Kaam ko automatically schedule karna — cron aur at.",
      "keywords": ["cron", "Schedule", "Automation"],
      "points": ["crontab -e: schedule edit karte hain",
                 "5 fields: minute hour day month weekday",
                 "@daily, @weekly — easy presets bhi hain"]},
     {"title": "Command: at", "hook": "Ek baar ke liye schedule — at.",
      "cmd": "echo 'backup' | at 02:00", "note": "One-time jobs ke liye at"}),
    ("Advanced",
     {"title": "Shell One-liners", "hook": "Ek line mein complex kaam — shell one-liners, aapka speed boost.",
      "keywords": ["One-liners", "Shortcuts", "Speed"],
      "points": ["&&, ||, ;: control flow ek line mein",
                 "$(command): command substitution",
                 "History: !! aur !$ shortcuts"]},
     {"title": "Command: history", "hook": "Aapne kya chalaya — history.",
      "cmd": "history | tail -20", "note": "!! last command repeat karta hai"}),
    ("Advanced",
     {"title": "Containers Ki Shuruaat", "hook": "Apps ko portable banana — containers, aaj basics pe.",
      "keywords": ["Containers", "Docker", "Portable"],
      "points": ["Container: app + dependencies ek packet mein",
                 "docker run: ek command mein app chalu",
                 "Images aur containers — basic terminology"]},
     {"title": "Command: docker", "hook": "Images dekhna — docker images.",
      "cmd": "docker images", "note": "docker run -d -p 80:80 nginx"}),
    ("Advanced",
     {"title": "SSH Aur Remote Access", "hook": "Dusre computer pe baith kar kaam karna — SSH ka magic.",
      "keywords": ["SSH", "Remote", "Servers"],
      "points": ["ssh user@host: remote login",
                 "scp: files copy remote aur local ke beech",
                 "Key-based auth password se safe hai"]},
     {"title": "Command: ssh", "hook": "Remote machine pe login — ssh.",
      "cmd": "ssh user@server-ip", "note": "ssh-keygen se key banwayein, phir koi password nahi"}),
    ("Advanced",
     {"title": "Capstone: Mini Tool Banaye", "hook": "Sab ki sab ek saath — aaj ek real mini tool banate hain.",
      "keywords": ["Capstone", "Project", "Grade"],
      "points": ["Variables, loops, conditionals, functions sab use hue",
                 "Script: backup + log check + notification",
                 "30-day series ka recap — aap Linux ready hain"]},
     {"title": "Command: ls -R", "hook": "Series ka aakhiri command — sab dekhte hain.",
      "cmd": "ls -R ~", "note": "Recursive sab folders dikhata hai"}),
]


# title -> terminal demo lines: {"t": "cmd"|"out"|"err", "text": "..."}
# shown on a dark terminal-window slide so viewers SEE the command + output
DEMOS = {
    # --- main lessons ---
    "Linux Kya Hai": [
        {"t": "cmd", "text": "uname -a"},
        {"t": "out", "text": "Linux user 6.8.0-45-generic #45-Ubuntu"},
        {"t": "out", "text": "x86_64 GNU/Linux"},
        {"t": "cmd", "text": "cat /etc/os-release | head -2"},
        {"t": "out", "text": "NAME=\"Ubuntu\" VERSION=\"24.04 LTS\""},
    ],
    "Terminal Pe Pehla Baar": [
        {"t": "cmd", "text": "pwd"},
        {"t": "out", "text": "/home/user"},
        {"t": "cmd", "text": "ls"},
        {"t": "out", "text": "Documents  Downloads  Music  notes.txt"},
    ],
    "Files Aur Directories": [
        {"t": "cmd", "text": "mkdir project"},
        {"t": "cmd", "text": "touch project/notes.txt"},
        {"t": "cmd", "text": "ls project"},
        {"t": "out", "text": "notes.txt"},
    ],
    "Permissions Ek Bar Samajh Lo": [
        {"t": "cmd", "text": "ls -l notes.txt"},
        {"t": "out", "text": "-rw-r--r-- 1 user user 1234 notes.txt"},
        {"t": "out", "text": "r w -  r w -  r w -  → rwx rights"},
    ],
    "Files Padhna": [
        {"t": "cmd", "text": "cat notes.txt"},
        {"t": "out", "text": "Hello Linux! Aaj file padh rahe hain."},
        {"t": "cmd", "text": "head -1 notes.txt"},
        {"t": "out", "text": "Hello Linux!"},
    ],
    "Help Aur Docs": [
        {"t": "cmd", "text": "ls --help | head -4"},
        {"t": "out", "text": "Usage: ls [OPTION]... [FILE]..."},
        {"t": "out", "text": "List information about the FILEs."},
    ],
    "Search Karo  Smartly": [
        {"t": "cmd", "text": "grep -i linux notes.txt"},
        {"t": "out", "text": "Hello Linux! ye line mili."},
        {"t": "cmd", "text": "find . -name '*.txt'"},
        {"t": "out", "text": "./notes.txt  ./readme.txt"},
    ],
    "Pipes Aur Redirection": [
        {"t": "cmd", "text": "ls | wc -l"},
        {"t": "out", "text": "3"},
        {"t": "cmd", "text": "ls > files.txt"},
        {"t": "out", "text": "(file save hui — khatam!)"},
    ],
    "Processes Ko Samajhna": [
        {"t": "cmd", "text": "ps aux | head -3"},
        {"t": "out", "text": "USER     PID %CPU COMMAND"},
        {"t": "out", "text": "user     42  0.0 bash"},
    ],
    "Vim Shuru Karo": [
        {"t": "cmd", "text": "vim notes.txt"},
        {"t": "out", "text": "~"},
        {"t": "out", "text": "~  notes.txt (INSERT mode)"},
        {"t": "out", "text": ":wq  → save karke exit"},
    ],
    "Permissions Ka Deep Dive": [
        {"t": "cmd", "text": "chmod 755 script.sh"},
        {"t": "cmd", "text": "ls -l script.sh"},
        {"t": "out", "text": "-rwxr-xr-x 1 user user script.sh"},
    ],
    "Copy, Move, Compare": [
        {"t": "cmd", "text": "cp a.txt b.txt"},
        {"t": "cmd", "text": "diff a.txt b.txt"},
        {"t": "out", "text": "(koi output nahi — dono same hai!)"},
    ],
    "Bash Ki Shuruaat": [
        {"t": "cmd", "text": "echo $HOME"},
        {"t": "out", "text": "/home/user"},
        {"t": "cmd", "text": "name=Linux; echo $name"},
        {"t": "out", "text": "Linux"},
    ],
    "Conditionals IF Else": [
        {"t": "cmd", "text": "if [ -f notes.txt ]; then echo \"file hai\"; fi"},
        {"t": "out", "text": "file hai"},
    ],
    "Loops For Aur While": [
        {"t": "cmd", "text": "for i in 1 2 3; do echo $i; done"},
        {"t": "out", "text": "1"},
        {"t": "out", "text": "2"},
        {"t": "out", "text": "3"},
    ],
    "Functions Aur Scripts": [
        {"t": "cmd", "text": "chmod +x script.sh"},
        {"t": "cmd", "text": "./script.sh"},
        {"t": "out", "text": "Hello from script!"},
    ],
    "Regex Ki Duniya": [
        {"t": "cmd", "text": "grep -E '[0-9]+' notes.txt"},
        {"t": "out", "text": "Line 42: backup done"},
        {"t": "out", "text": "Line 7: log checked"},
    ],
    "Aapka Pehla Script": [
        {"t": "cmd", "text": "./backup.sh"},
        {"t": "out", "text": "[1/3] Backup start"},
        {"t": "out", "text": "[2/3] Logs check"},
        {"t": "out", "text": "Backup complete ✅"},
    ],
    "Users Aur Groups": [
        {"t": "cmd", "text": "whoami"},
        {"t": "out", "text": "user"},
        {"t": "cmd", "text": "id"},
        {"t": "out", "text": "uid=1000(user) gid=1000(user)"},
    ],
    "Packages Install Karo": [
        {"t": "cmd", "text": "apt install htop"},
        {"t": "out", "text": "Reading package lists... Done"},
        {"t": "out", "text": "htop installed ✅"},
    ],
    "Services Aur systemd": [
        {"t": "cmd", "text": "systemctl status ssh"},
        {"t": "out", "text": "● ssh.service — OpenBSD Secure Shell"},
        {"t": "out", "text": "Active: active (running)"},
    ],
    "Networking Basics": [
        {"t": "cmd", "text": "ip addr | grep inet"},
        {"t": "out", "text": "inet 192.168.1.10/24 brd 192.168.1.255"},
        {"t": "cmd", "text": "ping -c 2 127.0.0.1"},
        {"t": "out", "text": "2 packets transmitted, 2 received"},
    ],
    "Disks Aur Filesystems": [
        {"t": "cmd", "text": "df -h"},
        {"t": "out", "text": "Filesystem Size Used Avail Use%"},
        {"t": "out", "text": "/dev/sda1  47G  20G  25G  46%"},
    ],
    "Logs Ko Read Karo": [
        {"t": "cmd", "text": "journalctl -n 2"},
        {"t": "out", "text": "Nov 27 09:15:01 systemd: Started Daily"},
        {"t": "out", "text": "Nov 27 09:15:02 user: session opened"},
    ],
    "sed Aur awk": [
        {"t": "cmd", "text": "sed 's/old/new/' file.txt"},
        {"t": "out", "text": "Welcome new Linux!"},
        {"t": "cmd", "text": "awk '{print $1}' file.txt"},
        {"t": "out", "text": "Welcome"},
    ],
    "Cron Aur Scheduling": [
        {"t": "cmd", "text": "crontab -l"},
        {"t": "out", "text": "0 9 * * * /home/user/backup.sh"},
        {"t": "out", "text": "roz 9 AM backup chalega"},
    ],
    "Shell One-liners": [
        {"t": "cmd", "text": "cd /tmp && pwd"},
        {"t": "out", "text": "/tmp"},
        {"t": "cmd", "text": "ls -la | head -2"},
        {"t": "out", "text": "total 42"},
    ],
    "Containers Ki Shuruaat": [
        {"t": "cmd", "text": "docker ps"},
        {"t": "out", "text": "CONTAINER ID  IMAGE     STATUS"},
        {"t": "out", "text": "a1b2c3d4e5f6  nginx    Up 2 minutes"},
    ],
    "SSH Aur Remote Access": [
        {"t": "cmd", "text": "ssh user@server-ip"},
        {"t": "out", "text": "user@server-ip's password:"},
        {"t": "out", "text": "Welcome to Ubuntu 24.04 (GNU/Linux)"},
    ],
    "Capstone: Mini Tool Banaye": [
        {"t": "cmd", "text": "./mini-tool.sh"},
        {"t": "out", "text": "[1/3] Backup done"},
        {"t": "out", "text": "[2/3] Logs checked"},
        {"t": "out", "text": "Mini tool ready ✅ Series complete!"},
    ],
    # --- command-of-the-day tips ---
    "Command: ls": [
        {"t": "cmd", "text": "ls -la"},
        {"t": "out", "text": "total 24"},
        {"t": "out", "text": "drwxr-xr-x 4 user user 4096 ."},
        {"t": "out", "text": "-rw-r--r-- 1 user user 1234 notes.txt"},
    ],
    "Command: cd": [
        {"t": "cmd", "text": "cd ~/Documents"},
        {"t": "cmd", "text": "pwd"},
        {"t": "out", "text": "/home/user/Documents"},
    ],
    "Command: mkdir": [
        {"t": "cmd", "text": "mkdir my-folder"},
        {"t": "cmd", "text": "ls"},
        {"t": "out", "text": "my-folder"},
    ],
    "Command: chmod": [
        {"t": "cmd", "text": "chmod 755 file.sh"},
        {"t": "cmd", "text": "ls -l file.sh"},
        {"t": "out", "text": "-rwxr-xr-x 1 user user file.sh"},
    ],
    "Command: tail": [
        {"t": "cmd", "text": "tail -n 3 app.log"},
        {"t": "out", "text": "09:15:01 INFO server started"},
        {"t": "out", "text": "09:15:02 INFO listening on 8080"},
        {"t": "out", "text": "09:15:03 INFO ready ✅"},
    ],
    "Command: man": [
        {"t": "cmd", "text": "man ls | head -5"},
        {"t": "out", "text": "NAME     ls — list directory contents"},
        {"t": "out", "text": "SYNOPSIS ls [OPTION]... [FILE]..."},
    ],
    "Command: find": [
        {"t": "cmd", "text": "find . -name '*.txt'"},
        {"t": "out", "text": "./notes.txt"},
        {"t": "out", "text": "./project/readme.txt"},
    ],
    "Command: grep | wc": [
        {"t": "cmd", "text": "grep -c error app.log"},
        {"t": "out", "text": "3"},
    ],
    "Command: top": [
        {"t": "cmd", "text": "top -n 1 | head -5"},
        {"t": "out", "text": "PID USER  %CPU COMMAND"},
        {"t": "out", "text": "1 root   0.0 init"},
        {"t": "out", "text": "42 user   1.2 bash"},
    ],
    "Command: vim": [
        {"t": "cmd", "text": "vim notes.txt"},
        {"t": "out", "text": "~  ~  ~"},
        {"t": "out", "text": "-- INSERT --  → :wq se exit"},
    ],
    "Command: umask": [
        {"t": "cmd", "text": "umask"},
        {"t": "out", "text": "0022"},
        {"t": "out", "text": "→ nayi files 644 default"},
    ],
    "Command: diff": [
        {"t": "cmd", "text": "diff a.txt b.txt"},
        {"t": "out", "text": "1c1"},
        {"t": "out", "text": "< old line"},
        {"t": "out", "text": "> new line"},
    ],
    "Command: echo": [
        {"t": "cmd", "text": "echo Hello Linux"},
        {"t": "out", "text": "Hello Linux"},
    ],
    "Command: test -f": [
        {"t": "cmd", "text": "[ -f notes.txt ] && echo yes"},
        {"t": "out", "text": "yes"},
        {"t": "cmd", "text": "[ -f missing.txt ] && echo yes"},
        {"t": "out", "text": "( kuch nahi — condition false)"},
    ],
    "Command: for": [
        {"t": "cmd", "text": "for f in *.txt; do echo $f; done"},
        {"t": "out", "text": "notes.txt"},
        {"t": "out", "text": "readme.txt"},
    ],
    "Command: chmod +x": [
        {"t": "cmd", "text": "chmod +x myscript.sh"},
        {"t": "cmd", "text": "./myscript.sh"},
        {"t": "out", "text": "Script chal gaya! ✅"},
    ],
    "Command: grep -E": [
        {"t": "cmd", "text": "grep -E '[0-9]+' app.log"},
        {"t": "out", "text": "log1: started"},
        {"t": "out", "text": "log42: ready"},
    ],
    "Command: crontab": [
        {"t": "cmd", "text": "crontab -l"},
        {"t": "out", "text": "0 9 * * * /home/user/backup.sh"},
    ],
    "Command: sudo": [
        {"t": "cmd", "text": "sudo whoami"},
        {"t": "out", "text": "root"},
        {"t": "out", "text": "→ admin powers, sirf jarurat pe"},
    ],
    "Command: apt": [
        {"t": "cmd", "text": "apt search htop"},
        {"t": "out", "text": "htop — interactive process viewer"},
    ],
    "Command: systemctl": [
        {"t": "cmd", "text": "systemctl is-active ssh"},
        {"t": "out", "text": "active"},
    ],
    "Command: curl": [
        {"t": "cmd", "text": "curl -s https://example.com | head -2"},
        {"t": "out", "text": "<!doctype html>"},
        {"t": "out", "text": "<html>"},
    ],
    "Command: du": [
        {"t": "cmd", "text": "du -sh /var/log"},
        {"t": "out", "text": "12M	/var/log"},
    ],
    "Command: journalctl": [
        {"t": "cmd", "text": "journalctl -n 2 --no-pager"},
        {"t": "out", "text": "Nov 27 09:15:01 systemd: Started Daily"},
        {"t": "out", "text": "Nov 27 09:15:02 sudo: session open"},
    ],
    "Command: sed": [
        {"t": "cmd", "text": "sed 's/old/new/' file.txt"},
        {"t": "out", "text": "Welcome new Linux!"},
    ],
    "Command: at": [
        {"t": "cmd", "text": "echo 'backup' | at 02:00"},
        {"t": "out", "text": "job 1 at Thu Nov 27 02:00:00 2026"},
    ],
    "Command: history": [
        {"t": "cmd", "text": "history | tail -3"},
        {"t": "out", "text": "101 ls -la"},
        {"t": "out", "text": "102 cd ~/Documents"},
        {"t": "out", "text": "103 vim notes.txt"},
    ],
    "Command: docker": [
        {"t": "cmd", "text": "docker images"},
        {"t": "out", "text": "REPOSITORY TAG  IMAGE ID  SIZE"},
        {"t": "out", "text": "nginx     latest  a1b2c3d4  190MB"},
    ],
    "Command: ssh": [
        {"t": "cmd", "text": "ssh user@server-ip"},
        {"t": "out", "text": "user@server-ip's password:"},
        {"t": "out", "text": "→ key-based auth = no password"},
    ],
    "Command: ls -R": [
        {"t": "cmd", "text": "ls -R ~ | head -8"},
        {"t": "out", "text": ".:"},
        {"t": "out", "text": "Documents  Downloads  notes.txt"},
        {"t": "out", "text": "./Documents:"},
    ],
}


def scaffold_episode(out_dir: Path, ep_no: int, day: int, phase: str,
                     main: dict, tip: dict) -> None:
    d = out_dir / f"episode_{ep_no:03d}"
    (d / "images").mkdir(parents=True, exist_ok=True)
    # main episode = even numbering, tip = odd
    kind = "tip" if ep_no % 2 == 0 else "main"
    data = tip if kind == "tip" else main
    badges = data.get("keywords") or [data.get("cmd", "Tip").split()[0], "Tip", "Daily"]
    # build slides spec
    slides = [{"kind": "hook", "title": data["title"], "sub": "Linux series — day %d" % day,
               "data": {"badges": badges, "tagline": data["hook"]}}]
    demo = DEMOS.get(data["title"])
    if kind == "main":
        slides.append({"kind": "list", "title": "Points", "sub": None,
                       "data": {"items": [f"{i+1}. {p}" for i, p in enumerate(data["points"])]}})
        if demo:
            slides.append({"kind": "terminal", "title": "Terminal Mein Dekho", "sub": None,
                           "data": {"title_bar": "bash — user@linux:~",
                                    "prompt": "user@linux:~$", "lines": demo}})
        slides.append({"kind": "summary", "title": "Yaad Rakhiye", "sub": None,
                       "data": {"lines": [{"text": p, "color": "blue"} for p in data["points"][:2]],
                                "badge": "agli class mein milte hain"}})
    else:
        slides.append({"kind": "blocks", "title": "Command of the Day", "sub": None,
                       "data": {"blocks": [{"head": data["cmd"], "body": data["note"], "color": "green"}]}})
        if demo:
            slides.append({"kind": "terminal", "title": "Terminal Mein Dekho", "sub": None,
                           "data": {"title_bar": "bash — user@linux:~",
                                    "prompt": "user@linux:~$", "lines": demo}})
        slides.append({"kind": "summary", "title": "Tip", "sub": None,
                       "data": {"lines": [{"text": data["note"], "color": "green"}],
                                "badge": "try it \u2713"}})
    (d / "slides_spec.json").write_text(
        json.dumps({"slides": slides}, indent=2, ensure_ascii=False), encoding="utf-8")
    # script.md in vs_plan format
    lines = [f"# Video: {data['title']}", "",
             f"## Scene 1 — Hook",
             f"| Visual    | Teacher whiteboard: title {data['title']} |",
             f"| Narration | {data['hook']} |",
             f"| Title     | {data['title']} |", ""]
    if kind == "main":
        for i, p in enumerate(data["points"], 2):
            lines += [f"## Scene {i} — Point {i-1}",
                      f"| Visual    | Teacher whiteboard: {p[:60]} |",
                      f"| Narration | {p} |",
                      f"| Title     | {p[:28]} |", ""]
        if demo:
            nxt = len(data["points"]) + 2
            cmds = [ln["text"] for ln in demo if ln.get("t") == "cmd"]
            demo_desc = ", ".join(cmds[:2]) if cmds else "command"
            lines += [f"## Scene {nxt} — Terminal Mein Dekho",
                      f"| Visual    | Terminal window: {demo_desc} chalta hua, output dikh raha hai |",
                      f"| Narration | Ab terminal mein dekhte hain — {demo_desc} chalta hai, output aapke samne hai. |",
                      f"| Title     | Terminal Mein Dekho |", ""]
        lines += [f"## Scene {len(data['points'])+3 if demo else len(data['points'])+2} — Wrap up",
                  f"| Visual    | Teacher whiteboard: summary |",
                  f"| Narration | Agli class mein milte hain. |",
                  f"| Title     | Agli Class Mein |", ""]
    else:
        lines += [f"## Scene 2 — Command of the Day",
                  f"| Visual    | Teacher whiteboard: {data['cmd']} with note |",
                  f"| Narration | {data['cmd']} — {data['note']}. |",
                  f"| Title     | {data['cmd']} |", ""]
        if demo:
            cmds = [ln["text"] for ln in demo if ln.get("t") == "cmd"]
            demo_desc = ", ".join(cmds[:2]) if cmds else data["cmd"]
            lines += [f"## Scene 3 — Terminal Mein Dekho",
                      f"| Visual    | Terminal window: {demo_desc} chalta hua, output dikh raha hai |",
                      f"| Narration | Ab terminal mein dekhte hain — {demo_desc} chalta hai, output aapke samne hai. |",
                      f"| Title     | Terminal Mein Dekho |", ""]
            lines += [f"## Scene 4 — Tip",
                      f"| Visual    | Teacher whiteboard: tip card |",
                      f"| Narration | Aaj hi terminal kholke try kar lo. Agli class mein milte hain! |",
                      f"| Title     | Try It |", ""]
        else:
            lines += [f"## Scene 3 — Tip",
                      f"| Visual    | Teacher whiteboard: tip card |",
                      f"| Narration | Aaj hi terminal kholke try kar lo. Agli class mein milte hain! |",
                      f"| Title     | Try It |", ""]
    (d / "script.md").write_text("\n".join(lines), encoding="utf-8")
    return


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="series")
    ap.add_argument("--episode", type=int, default=None,
                    help="scaffold only one episode number (1-based)")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.episode:
        idx = args.episode - 1
        day = idx // 2 + 1
        phase, main, tip = CURRICULUM[idx % len(CURRICULUM)]
        scaffold_episode(out, args.episode, day, phase, main, tip)
        print(f"episode_{args.episode:03d} scaffolded")
        return 0

    plan = ["# Linux Series — 30 Days, Beginner to Advanced (Instagram Reels)",
            "",
            "Daily: 1 main lesson Reel + 1 command-of-the-day tip Reel.",
            "Each episode folder: script.md + slides_spec.json → produce with",
            "vs_slides.py → vs_plan.py → narration → vs_audio.py → vs_render.py",
            "→ ig-reels.py → ig_caption.py",
            "",
            "| Day | Phase | Ep | Title | Hook |",
            "|---|---|---|---|---|"]
    for i, (phase, main, tip) in enumerate(CURRICULUM):
        day = i + 1
        scaffold_episode(out, i * 2 + 1, day, phase, main, tip)
        scaffold_episode(out, i * 2 + 2, day, phase, main, tip)
        plan.append(f"| {day} | {phase} | {i*2+1} | {main['title']} | {main['hook'][:60]} |")
        plan.append(f"| {day} | {phase} | {i*2+2} | {tip['title']} | {tip['hook'][:60]} |")
    (out / "series_plan.md").write_text("\n".join(plan) + "\n", encoding="utf-8")
    print(f"series planned: {len(CURRICULUM)} days, {len(CURRICULUM)*2} episodes")
    print(f"series_plan.md written, episode_001..episode_{len(CURRICULUM)*2:03d} scaffolded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
