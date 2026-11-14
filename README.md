# BILLY5000

The Bixler family world clock. 64×32 RGB LED matrix, Raspberry Pi + Adafruit Bonnet.

## Layout

```
BILLY5000/
  main.py            starts the clock, runs the page rotation
  settings.py        places, colors, timing, brightness  <- edit this one
  engine/            panel/emulator plumbing and drawing helpers (rarely touched)
  pages/             one file per kind of screen
    __init__.py      the lineup: which pages show, in what order
    city.py          place page: code, time, weather, name
    alert.py         NOAA alert explanation page (only when one is active)
    sports.py        one page per team + the ITFDB flash
    santa.py         hooks the Santa Alert and Christmas radar into the clock
    seattle_weather.py  Seattle NOW, 12 HR and 5 DAY pages
    flagquiz.py      flag quiz (flags drawn in engine/flags.py)
    bells.py         ship's bells every half hour
    special.py       special days, trash day, countdown (drawing in engine/specialdays.py)
  fonts/             .bdf fonts
  run.ps1            run on your PC in the browser emulator
  billy5000.service  auto-start on the Pi
```

## Rules of the road

1. **One file per feature.** Weather, tides, sports and Santa each get their own file in `pages/`. No more 2,000-line files.
2. **No more test copies.** No `test2.py` or `test64_final.py`. Git keeps every old version, so make a branch to try something risky.
3. **A broken page never kills the clock.** The main loop logs the error and moves to the next page.
0. **Startup screen:** BILLY5000 boot check + logo plays once at launch (`STARTUP_SPLASH` in settings.py).
4. **`--at` previews any moment:** `.\run.ps1 --at "2026-12-24 18:00"`.
5. **`--demo-alerts` previews the red alert look:** `.\run.ps1 --demo-alerts`.
6. **`--demo-sports` previews the sports pages; `--demo-itfdb` plays the Dodgers flash.**
7. **`--demo-weather` previews the Seattle weather pages with a sample forecast.**
8. **`--demo-santa` runs a Santa TOY alert now.** Santa's own settings (messages, sightings, how often) are at the top of `engine/santa.py`.

## On the PC

```powershell
.\run.ps1          # then open http://localhost:8888
```

## On the Pi (first time)

Flash Raspberry Pi OS Lite (64-bit) with Imager (hostname BILLY5000, user mbixler, Wi-Fi, SSH on), then:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-venv
python3 -m venv ~/env --system-site-packages && source ~/env/bin/activate
pip3 install adafruit-python-shell click
wget https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/raw/main/rgb-matrix.py
sudo -E env PATH=$PATH python3 rgb-matrix.py    # Bonnet, Convenience, reboot
ssh-keygen -t ed25519 -C "billy5000" -N "" -f ~/.ssh/id_ed25519 && cat ~/.ssh/id_ed25519.pub
#   -> add that line as a read-only deploy key on GitHub
git clone git@github.com:mbixler10/BILLY5000.git ~/BILLY5000
cd ~/BILLY5000
sudo ~/env/bin/python3 main.py            # test it; Ctrl+C to stop
sudo cp billy5000.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now billy5000
```

Update after a push from the PC:

```bash
cd ~/BILLY5000 && git pull && sudo systemctl restart billy5000
journalctl -u billy5000 -f                # watch the log
```

## Features to move over from deskclock (one at a time)

- [x] Place pages with Home every 4th page
- [x] Weather on place pages (Open-Meteo)
- [x] Seattle NOW / 12 HR / 5 DAY weather pages
- [x] NOAA alerts: red bar + explanation page
- [x] Special days: holiday colors, greetings, flag days, birthdays, anniversary, April Fools
- [x] Trash day + countdown to the next special day
- [ ] Tides (NOAA)
- [x] Sports block (ESPN), including the ITFDB flash
- [x] Santa Alert (ELFNET / TOY)
- [ ] Ship's watch names
- [x] Flag game: 87 countries + 7 US states (random, guess then stamp)
- [x] Nautical lesson: 26 letter flags + 10 numeral pennants, one per lap, A-Z then 0-9
- [x] Lighthouse lesson: 58 lighthouses blink their real light pattern, one per lap at a random spot (`python main.py --lighthouse "NORTH HEAD"` to preview)
- [x] Date on city pages (each city shows its own date) and the Peter & Katie Hong Kong page
- [x] V3.1: date spacing on city pages, hand-set colors for small-college opponents (COLLEGE_COLORS)
- [x] Olympic countdown to LA28 + tribute to Great-Grandpa Dallas Bixler (1932 gold, horizontal bar), every 3rd lap
- [x] Veterans Day honor roll (scrolling) and 9/11 reading of the names from 8:46 AM ET, one name at a time (run tools/get_911_names.py once)
- [x] V3.3: faster lighthouse page, lighter tickers, Home every 4th page that actually shows (alerts never count, one alert per visit); 9/11 reading on hold
- [x] Pearl Harbor Day reading of the names (Dec 7, from 7:48 AM Hawaii time = 9:48 AM Seattle): 2,408 names by ship and station, USS ARIZONA first, with rank and service; about 2 hours. Names in data/names_pearl_harbor.txt (rebuild with tools/pearl_from_xlsx.py)
- [x] V4.0: slower, busier start-up (RAM test, team cries in STARTUP_CHANTS, STARTUP_PACE); Opening Day Mode (Uncle Buck's idea): countdown from a week after the World Series, jersey-number countdown from 99 days (`data/jersey_countdown.txt`), milestone cards, Opening Day takeover, ballpark-themed clocks all Opening Day week + Uncle Buck's credit, new live baseball scoreboard (bases, count, outs, who's up), HOME RUN!! flash. Dates in settings.py (OPENING_DAYS). `python -m engine.baseball all` lists every countdown day.
- [x] V4.1: Hanukkah (menorah counts the nights), overlapping holidays take turns a lap each, every holiday gets its own Home message (home_label), better contrast on Halloween/Thanksgiving/Boxing Day, and ~30 new days: MLK, Lunar New Year, Scouting's birthday, Super Bowl, Mardi Gras, Leap Day, daylight saving reminders, Pi Day, the four seasons (with Seattle sunrise/sunset), Purim, Easter, Passover, Earth Day, boating's Opening Day, Kentucky Derby, Mother's/Father's Day, Dog Day, Rosh Hashanah, Pirate Day, Yom Kippur, Sukkot, Navy birthday, New Year's Eve, Rose Bowl, Pearl Harbor, and a full-moon page. Sky math in engine/sky.py; drawn pages in engine/holiday_art.py.
- [ ] Calendar
