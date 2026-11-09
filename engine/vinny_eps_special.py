"""
Vinny episodes, part 3: CHRISTMAS EVE, CHRISTMAS DAY and the BOXING DAY special.
"""
from engine.vinnykit import *

A, G, Y, Wt, R, B, P, C_ = AMBER, GREEN, GOLD, WHITE, RED, BLUE, PINK, CYAN
SNOW = 15
FLOOR = 17

EVE = [
    Ep("final_report", "eve", "FINAL REPORT", 9, "blueprint",
       say(0, "FINAL REPORT", A),
       say(1, "SUBJECT:", Wt, at=0.8), say(1, "BILLY", Y, at=1.6, x=40, typed=False),
       say(2, "NICE LIST:", Wt, at=2.2),
       draw(lambda c, t: (box(6, 24, 57, 31, R)(c, t), text(c, 9, 31, R, "APPROVED")), at=3.6),
       fx("fireworks", at=4.4)),
    Ep("santa_snacks", "eve", "SANTA SNACKS", 9, "room",
       spr("plate", 24, 26),
       spr("cookie", 26, 21, at=0.6), spr("cookie", 32, 21, at=1.2), spr("cookie", 38, 21, at=1.8),
       spr("milk", 46, 20, at=2.4), spr("carrot", 14, 24, at=3.0),
       vin(4, FLOOR, "stand", until=4.0),
       vin(4, FLOOR, "up", at=4.0),
       say(0, "SANTA SNACKS", A),
       say(1, "+ RUDOLPH", G, at=3.0, x=14, size="t"),
       say(3, "", Wt)),
    Ep("pack_home", "eve", "PACKING UP", 9, "room",
       spr("suitcase", 26, 22),
       spr("coffee", 8, 10, path=[(0.5, 8, 10), (1.2, 28, 4), (1.6, 28, 20)], until=1.6),
       spr("sock", 8, 10, path=[(1.6, 8, 10), (2.3, 28, 4), (2.7, 28, 20)], at=1.6, until=2.7),
       spr("needle", 6, 8, path=[(2.7, 6, 8), (3.4, 28, 0), (3.9, 28, 16)], at=2.7, until=3.9),
       vin(44, FLOOR, "stand"),
       say(0, "SOUVENIRS:", A),
       count(52, 15, 0, 3, run=(0.5, 4.0), col=G),
       say(3, "1 SOCK (S.)", Y, at=4.6, x=1, size="t")),
    Ep("sleigh_pickup", "eve", "PICKUP", 10, "night",
       fx("stars", n=18), spr("moon", 46, 3),
       vin(8, FLOOR, "wave", until=4.0),
       spr("reindeer", -30, 8, to=(16, 12), move=(0.5, 4.0)),
       spr("sleigh", -20, 14, to=(26, 18), move=(0.5, 4.0), until=4.2),
       spr("reindeer", 16, 12, at=4.0, to=(90, -6), move=(4.6, 7.6)),
       group(spr("sleigh", 26, 18, at=4.2, to=(100, 0), move=(4.6, 7.6)),
             vin(28, 6, "wave", at=4.2, to=(102, -12), move=(4.6, 7.6))),
       say(None, "BYE BILLY!", Y, at=5.0, x=1, y=31),
       say(None, "SEE YOU", G, at=6.6, x=1, y=16, size="t"),
       say(None, "NEXT YEAR!", G, at=7.2, x=1, y=23, size="t")),
]

XMAS = [
    Ep("home_asleep", "xmas", "SHIFT OVER", 9, "pole",
       spr("igloo", 24, 22),
       spr("v_sleep", 30, 15, at=0),
       fx("zzz", x=38, y=14),
       say(0, "MISSION DONE", A),
       say(None, "DO NOT", Wt, at=2.0, x=1, y=23, size="t"),
       say(None, "DISTURB", R, at=2.6, x=1, y=29, size="t")),
    Ep("mission_success", "xmas", "SUCCESS", 9, "pole",
       vin(26, SNOW, "up", hop=2),
       fx("confetti", n=40),
       say(0, "MERRY", R, center=True, typed=False, blink=0.6),
       say(1, "CHRISTMAS", G, at=0.6, center=True),
       say(None, "BILLY!", Y, at=1.6, x=1, y=31)),
]

BOXING = [
    Ep("boxing_day", "boxing", "BOXING DAY", 14, "ring",
       say(0, "BOXING DAY!", A, until=3.0),
       spr("box_angry", 44, 18, until=8.6),
       vin(12, 15, "stand", until=3.0),
       spr("boxing_glove", 17, 22, until=3.0),
       spr("bell", 29, 4, at=3.0, until=4.0, shake=1),
       say(0, "DING!", Y, at=3.0, until=4.0, typed=False, x=40),
       vin(12, 15, "up", at=4.0, until=7.0, path=[(4.0, 12, 15), (4.6, 34, 15), (5.2, 26, 15), (5.8, 36, 15), (6.4, 24, 15)]),
       spr("boxing_glove", 20, 18, at=4.0, until=7.0, path=[(4.0, 20, 18), (4.6, 42, 18), (5.2, 32, 18), (5.8, 43, 18), (6.4, 30, 18)]),
       say(None, "POW!", R, at=4.6, until=5.2, x=45, y=15, typed=False),
       say(None, "BAM!", R, at=5.8, until=6.4, x=45, y=15, typed=False),
       say(0, "THE BOX:", Wt, at=7.0, until=8.6, typed=False),
       say(1, "UNHURT.", Y, at=7.6, until=8.6, typed=False),
       spr("box_angry", 44, 18, at=8.6, path=[(8.6, 44, 18), (9.2, 22, 18)]),
       vin(22, 15, "shock", at=7.0, until=9.2),
       spr("box", 18, 18, at=9.2),
       spr("elf_hat", 22, 14, at=9.2, blink=0.6),
       say(0, "WINNER:", A, at=9.4, typed=False),
       say(1, "THE BOX", R, at=10.0, typed=False),
       say(3, "HAPPY BOXING DAY", G, at=11.0, size="t", center=True)),
]
