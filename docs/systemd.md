# systemd

```shell
$ mkdir -pv ~/.config/systemd/user
mkdir: created directory '/home/cees/.config/systemd'
mkdir: created directory '/home/cees/.config/systemd/user/'
```

```shell
$ cat  ~/.config/systemd/user/trader.service
[Unit]
Description=Trader Service

[Service]
Type=oneshot
Environment=PYTHONPATH=/home/cees/prj/trdr/src/main/python
ExecStart=/home/cees/prj/trdr/venv/bin/python3 -m trdr.populate

[Install]
WantedBy=default.target
```

```shell
$ cat  ~/.config/systemd/user/trader.timer
[Unit]
Description=Trader Service Timer
Requires=trader.service

[Timer]
Unit=trader.service
OnCalendar=*-*-* 01:45:00

[Install]
WantedBy=timers.target
```

```shell
$ sudo loginctl enable-linger cees
$ sudo loginctl show-user cees
UID=1000
GID=1000
Name=cees
Timestamp=Sat 2021-09-25 21:12:30 CEST
TimestampMonotonic=77149461
RuntimePath=/run/user/1000
Service=user@1000.service
Slice=user-1000.slice
Display=1
State=active
Sessions=1
IdleHint=no
IdleSinceHint=1632598824797255
IdleSinceHintMonotonic=1751477601
Linger=yes
```

```shell
$ systemctl --user daemon-reload
$ systemctl --user enable trader.timer
$ systemctl --user start trader.timer
$ systemctl --user status trader.timer
● trader.timer - Trader Service Timer
     Loaded: loaded (/home/cees/.config/systemd/user/trader.timer; enabled; vendor preset: enabled)
     Active: active (waiting) since Sat 2021-09-25 21:42:04 CEST; 7s ago
    Trigger: Sat 2021-09-25 21:43:00 CEST; 48s left
   Triggers: ● trader.service

Sep 25 21:42:04 asrv0000019 systemd[760]: Started Trader Service Timer.
```

```shell
$ systemctl --user status
● asrv0000019
    State: running
     Jobs: 0 queued
   Failed: 0 units
    Since: Sat 2021-09-25 21:12:30 CEST; 40min ago
   CGroup: /user.slice/user-1000.slice/user@1000.service
           └─init.scope
             ├─760 /lib/systemd/systemd --user
             └─761 (sd-pam)
$ systemctl --user status trader.service
● trader.service - Trader Service
     Loaded: loaded (/home/cees/.config/systemd/user/trader.service; disabled; vendor preset: enabled)
     Active: inactive (dead) since Sat 2021-09-25 21:52:10 CEST; 1min 11s ago
TriggeredBy: ● trader.timer
   Main PID: 1761 (code=exited, status=0/SUCCESS)
        CPU: 371ms

Sep 25 21:52:10 asrv0000019 systemd[760]: Starting Trader Service...
Sep 25 21:52:10 asrv0000019 systemd[760]: trader.service: Succeeded.
Sep 25 21:52:10 asrv0000019 systemd[760]: Finished Trader Service.
$ systemctl --user status trader.timer
● trader.timer - Trader Service Timer
     Loaded: loaded (/home/cees/.config/systemd/user/trader.timer; enabled; vendor preset: enabled)
     Active: active (waiting) since Sat 2021-09-25 21:42:04 CEST; 11min ago
    Trigger: Sun 2021-09-26 01:45:00 CEST; 3h 51min left
   Triggers: ● trader.service

Sep 25 21:42:04 asrv0000019 systemd[760]: Started Trader Service Timer.
```