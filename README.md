### Create rf_coder.ini
```ini
[CODES]
;
pi3kitchen_on = xxx
pi3kitchen_off = xxx
;
stammen_pink_on = xxx
stammen_pink_off = xxx
;
stammen_green_on = xxx
stammen_green_off = xxx
```

### Create, enable and start services
- Copy ```home_remote.sevices``` file.
  ```bash
  cd home_remote
  cp linux-sevices/home_remote.services /etc/systemd/system/home_remote.service
  ```
- Customize path to ```main.py```.
  ```bash
  sudo nano /etc/systemd/system/home_remote.service
  ```
- Start and enable service.
  ```bash
  sudo systemctl enable home_remote.service
  sudo systemctl start home_remote.service
  ```