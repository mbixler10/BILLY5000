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

```bash
git clone git@github.com:mbixler10/BILLY5000.git ~/BILLY5000
cd ~/BILLY5000
sudo python3 main.py                      # test it; Ctrl+C to stop
sudo cp billy5000.service /etc/systemd/system/
sudo systemctl enable --now billy5000     # starts now and on every boot
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
- [ ] Calendar
