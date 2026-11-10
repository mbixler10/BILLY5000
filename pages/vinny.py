"""
Agent Vinny's ELFNET traffic as a takeover, side by side with Santa's TOY alerts.
Everything Vinny lives in engine/vinny.py.
"""
import random
import time

from engine import vinny
from .base import Page

KINDS = ["post", "sitrep", "intel", "santa", "orders", "intercept"]


class VinnyAlert(Page):
    def __init__(self):
        self.scenes = None
        self.started = 0.0
        self.force = None           # --demo-vinny [kind]: play one right away

    def is_active(self, now):
        if self.scenes is None:
            kind = None
            if self.force:
                kind = self.force if self.force in vinny_kinds() else random.choice(KINDS)
                self.force = None
            else:
                kind = vinny.due(now)
            if kind:
                self.scenes = vinny.transmission(kind, now)
                self.started = time.monotonic()
        return self.scenes is not None

    def draw(self, canvas, now, t):
        scene, local_t = vinny.scene_at(self.scenes, time.monotonic() - self.started)
        if scene is None:           # END TRAFFIC: hand the screen back
            self.scenes = None
            return
        scene(canvas, local_t)


def vinny_kinds():
    return KINDS + ["teaser", "deploy", "arrival", "arrival_santa", "eve_post", "eve_report",
                    "eve_santa", "eve_orders", "xmas"]
