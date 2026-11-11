"""
BILLY5000: Bixler family world clock.

Run on PC:   .\\run.ps1                      (opens emulator at http://localhost:8888)
Run on Pi:   sudo python3 main.py
Fake time:   python main.py --at "2026-12-24 18:00"    (preview any date/time)
Fake alerts: python main.py --demo-alerts              (preview the red alert look)
Fake sports: python main.py --demo-sports              (preview the sports pages)
ITFDB test:  python main.py --demo-itfdb               (play the Dodgers flash now)
Weather:     python main.py --demo-weather             (sample Seattle forecast)
Flag test:   python main.py --flag "SIGNAL B"          (or --flag JAPAN, or --flag signals)
Bells test:  python main.py --demo-bells               (strike the ship's bells now)
Lighthouse:  python main.py --lighthouse "NORTH HEAD"     (or --lighthouse all)
Santa test:  python main.py --demo-santa               (run a TOY alert now; add --at for other dates)
Vinny test:  python main.py --demo-vinny intercept     (one of Vinny's ELFNET transmissions now)
             python -m engine.vinny 2026-12-10         (Vinny's schedule for a day)
Opening Day: python main.py --demo-opening             (the Opening Day takeover now)
             python main.py --demo-homer MARINERS      (HOME RUN!! flash; add --grand)
             python main.py --demo-sports              (includes a live Dodgers game with bases/count)
             python main.py --at "2027-01-31 10:00"    (countdown / jersey for that day)
             python -m engine.baseball all             (every countdown day and its jersey)
"""
import argparse
import logging
import signal
import time
from datetime import datetime

import settings
from engine.display import Display
from engine import weather, alerts, sports, seattle_weather, medals
import pages
from pages import (build_rotation, TAKEOVERS, SANTA_ALERT, VINNY_ALERT, SHIPS_BELLS,
                   OPENING_ALERT, HOMER_FLASH)

FPS = 20


def flag_preview(which):
    """--flag: loop the flag quiz on just one flag, or every signal flag."""
    from pages.flagquiz import FlagQuiz
    from engine.nautical import SIGNALS
    q = FlagQuiz()
    names = ([f"SIGNAL {k}" for k in SIGNALS] if which.lower() == "signals"
             else [which.upper()])
    q.deck = list(reversed(names)) * 50
    return q


def lighthouse_preview(which):
    """--lighthouse: loop the lighthouse lesson on one lighthouse, or all of them."""
    from pages.lighthouse import LighthouseSlot, PICKER
    from engine.lighthouses import LIGHTHOUSES, get
    slot = LighthouseSlot()
    PICKER.pick = slot.i
    rows = list(LIGHTHOUSES) if which.lower() == "all" else [get(which.upper())]
    if rows == [None]:
        raise SystemExit("No lighthouse called %r - see engine/lighthouses.py" % which)
    PICKER.deck = list(reversed(rows)) * 50
    return slot


log = logging.getLogger("billy5000")


def make_clock(at):
    """Returns a now() function. With --at, time starts at that moment and keeps ticking."""
    if not at:
        return lambda: datetime.now().astimezone()
    start_fake = datetime.fromisoformat(at).astimezone()
    start_real = time.monotonic()
    from datetime import timedelta
    return lambda: start_fake + timedelta(seconds=time.monotonic() - start_real)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo-alerts", action="store_true",
                    help="show fake NOAA alerts for SEA and ARV to preview the look")
    ap.add_argument("--demo-sports", action="store_true",
                    help="show fake games to preview the sports pages")
    ap.add_argument("--demo-itfdb", action="store_true",
                    help="play the Dodgers ITFDB flash right at startup")
    ap.add_argument("--demo-santa", action="store_true",
                    help="run a Santa TOY alert right at startup")
    ap.add_argument("--demo-vinny", metavar="KIND", nargs="?", const="any",
                    help="play one of Agent Vinny's ELFNET transmissions now: sitrep, intel, "
                         "santa, orders, post, intercept, arrival, eve_report, xmas (default: random)")
    ap.add_argument("--demo-opening", action="store_true",
                    help="play the Opening Day takeover now, with sample games")
    ap.add_argument("--demo-homer", metavar="TEAM", nargs="?", const="DODGERS",
                    help="play the HOME RUN!! flash now (DODGERS or MARINERS)")
    ap.add_argument("--grand", action="store_true", help="with --demo-homer: make it a grand slam")
    ap.add_argument("--demo-weather", action="store_true",
                    help="use a sample Seattle forecast to preview the weather pages")
    ap.add_argument("--demo-bells", action="store_true",
                    help="strike the ship's bells right after startup")
    ap.add_argument("--flag", metavar="NAME",
                    help='preview flag quiz pages only, e.g. --flag "SIGNAL B", --flag JAPAN, '
                         'or --flag signals for all signal flags')
    ap.add_argument("--lighthouse", metavar="NAME",
                    help='preview the lighthouse lesson only, e.g. --lighthouse "NORTH HEAD" or --lighthouse all')
    ap.add_argument("--at", help='pretend it is this time, e.g. "2026-12-24 18:00"')
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    now = make_clock(args.at)
    display = Display(settings.PANEL)
    lineup = build_rotation()
    if args.flag:
        lineup = [flag_preview(args.flag)]
    if args.lighthouse:
        lineup = [lighthouse_preview(args.lighthouse)]
    weather.start()
    if args.demo_weather:
        seattle_weather.demo()
    else:
        seattle_weather.start()
    alerts.start(demo_mode=args.demo_alerts)
    medals.start()
    sports.start(demo_mode=args.demo_sports)
    if args.demo_itfdb:
        sports.trigger_itfdb()
    if args.demo_santa:
        SANTA_ALERT.force = True
    if args.demo_vinny:
        VINNY_ALERT.force = args.demo_vinny
    if args.demo_bells:
        SHIPS_BELLS.force = True
    if args.demo_opening:
        from pages.opening import demo_games
        OPENING_ALERT.demo_games = demo_games(now())
        OPENING_ALERT.force_at = True
    if args.demo_homer:
        HOMER_FLASH.force = args.demo_homer.upper()
        HOMER_FLASH.grand = args.grand

    running = True

    def stop(*_):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    log.info("BILLY5000 online: %d pages in rotation", len(lineup))
    i = 0
    while running:
        page = lineup[i % len(lineup)]
        i += 1
        if not page.is_active(now()):
            continue
        pages.shown(page)            # counts toward when Home comes around again
        seconds = page.seconds or settings.PAGE_SECONDS
        started = time.monotonic()
        last = started
        while running and (t := time.monotonic() - started) < seconds:
            canvas = display.new_frame()
            n = now()
            takeover = next((tk for tk in TAKEOVERS
                             if tk.is_active(n) and not tk.yields_to(page)), None)
            frame_start = time.monotonic()
            if takeover and getattr(page, "pause_on_takeover", False):
                started += frame_start - last          # page's clock stands still underneath
                t = frame_start - started
            last = frame_start
            try:
                if takeover:
                    takeover.draw(canvas, n, time.monotonic())
                else:
                    page.draw(canvas, n, t)
            except Exception:
                # one broken page never takes down the clock
                log.exception("%s failed; skipping it", type(takeover or page).__name__)
                break
            display.show()
            time.sleep(1 / FPS)

    display.clear()
    log.info("BILLY5000 offline")


if __name__ == "__main__":
    main()
