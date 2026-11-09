"""
Vinny & Buddy hookup: the FIELD LINK takeover, side by side with SantaAlert.
Everything Vinny lives in engine/vinny.py.
"""
import time

from engine import vinny
from .base import Page


class VinnyAlert(Page):
    def __init__(self):
        self.scenes = None
        self.started = 0.0
        self.force = False          # --demo-vinny sets this to run one right away
        self.episode = None         # --vinny-ep picks the episode for the demo

    def is_active(self, now):
        if self.scenes is None and (self.force or vinny.should_alert(now)):
            demo, self.force = self.force, False
            self.scenes = vinny.scenes(now, episode=self.episode if demo else None)
            self.started = time.monotonic()
        return self.scenes is not None

    def draw(self, canvas, now, t):
        scene, local_t = vinny.scene_at(self.scenes, time.monotonic() - self.started)
        if scene is None:           # END OF LINK done: hand the screen back
            self.scenes = None
            return
        scene(canvas, local_t)
