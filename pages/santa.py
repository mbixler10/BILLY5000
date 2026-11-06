"""
Santa Alert hookup. Everything Santa (scenes, messages, sightings, settings)
lives in engine/santa.py, which is your santa.py almost unchanged.

  SantaAlert  = takeover: the full ELFNET / TOY message sequence, a couple of
                times an hour in daytime from Nov 1 through Christmas Eve.
  SantaRadar  = a normal page that joins the rotation Dec 24-25: the radar
                scope, then MISSION COMPLETE on Christmas morning.
"""
import time

from engine import santa
from .base import Page


class SantaAlert(Page):
    def __init__(self):
        self.scenes = None
        self.started = 0.0
        self.force = False          # --demo-santa sets this to run one right away

    def is_active(self, now):
        if self.scenes is None and (self.force or santa.should_alert(now)):
            self.force = False
            self.scenes = santa.eam_scenes(now)
            self.started = time.monotonic()
        return self.scenes is not None

    def draw(self, canvas, now, t):
        scene, local_t = santa.scene_at(self.scenes, time.monotonic() - self.started)
        if scene is None:           # END OF MSG done: hand the screen back
            self.scenes = None
            return
        scene(canvas, local_t)


class SantaRadar(Page):
    seconds = santa.RADAR_SECONDS

    def is_active(self, now):
        return santa.tracker_page_active(now)

    def draw(self, canvas, now, t):
        santa.draw_page(canvas, now, t)
