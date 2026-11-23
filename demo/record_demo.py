#!/usr/bin/env python3
"""Drive the Kolektif gnoweb UI over CDP while ffmpeg records the X display.

Emits a JSON timeline of every action with its measured second, so narration
and captions can be placed on the real click instead of a guess.
"""
import json
import time
import urllib.request

from websocket import create_connection

BASE = "http://127.0.0.1:8888/r/g1udyt8ywv489087rn5td39m8t3peve3hxjz08w2/kolektif"
TIMELINE = []
T0 = None


def now():
    global T0
    if T0 is None:
        T0 = time.time()
    return round(time.time() - T0, 2)


class Cdp:
    def __init__(self, port=9222):
        for _ in range(60):
            try:
                pages = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                page = [p for p in pages if p["type"] == "page"][0]
                break
            except Exception:
                time.sleep(1)
        else:
            raise SystemExit("no CDP page")
        self.ws = create_connection(page["webSocketDebuggerUrl"], timeout=30)
        self.id = 0

    def send(self, method, **params):
        self.id += 1
        self.ws.send(json.dumps({"id": self.id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.id:
                return msg.get("result", {})

    def js(self, expr):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True)
        return r.get("result", {}).get("value")

    def wait_for(self, expr, timeout=25):
        end = time.time() + timeout
        while time.time() < end:
            if self.js(expr):
                return True
            time.sleep(0.4)
        return False

    def move(self, x, y, steps=12):
        """Move the X11 pointer so the recording shows a cursor approaching."""
        for i in range(1, steps + 1):
            self.send(
                "Input.dispatchMouseEvent",
                type="mouseMoved",
                x=x * i / steps,
                y=y * i / steps,
            )
            time.sleep(0.02)

    def click(self, x, y):
        self.move(x, y)
        self.send("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y,
                  button="left", clickCount=1)
        self.send("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y,
                  button="left", clickCount=1)

    def wheel(self, x, y, dy):
        self.send("Input.dispatchMouseEvent", type="mouseWheel", x=x, y=y,
                  deltaX=0, deltaY=dy)


def link_rect(cdp, text, index=0):
    expr = f"""(() => {{
      const links = [...document.querySelectorAll('a')]
        .filter(a => (a.innerText || '').trim().toLowerCase().includes({json.dumps(text.lower())}));
      const el = links[{index}];
      if (!el) return null;
      el.scrollIntoView({{block: 'center'}});
      const r = el.getBoundingClientRect();
      return {{x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}};
    }})()"""
    for _ in range(20):
        rect = cdp.js(expr)
        if rect:
            return rect
        time.sleep(0.4)
    return None


def record(step, label):
    TIMELINE.append({"step": step, "label": label, "at": now()})


def main():
    cdp = Cdp()
    cdp.send("Page.enable")
    cdp.send("Runtime.enable")
    cdp.send("Emulation.setDeviceMetricsOverride", width=1440, height=900,
             deviceScaleFactor=1, mobile=False)

    print("waiting for index...", flush=True)
    cdp.wait_for("document.body.innerText.includes('Kolektif')")
    record(1, "index: rotating savings circles, live stats")
    time.sleep(5)

    # scroll the index so both circle cards are seen
    for _ in range(6):
        cdp.wheel(720, 500, 220)
        time.sleep(0.55)
    record(2, "index: open and completed circles")
    time.sleep(2.5)

    # open the active circle
    rect = link_rect(cdp, "Enter circle", 0)
    if rect:
        cdp.click(rect["x"], rect["y"])
        cdp.wait_for("document.body.innerText.includes('Pot due this round')")
        record(3, "active circle: pot, deadline, member table")
        time.sleep(6)
        for _ in range(4):
            cdp.wheel(720, 500, 240)
            time.sleep(0.5)
        time.sleep(3)

    # back to the index, then the completed circle
    cdp.send("Page.navigate", url=BASE)
    cdp.wait_for("document.body.innerText.includes('Circles')")
    time.sleep(2)
    rect = link_rect(cdp, "Enter circle", 1)
    if rect:
        cdp.click(rect["x"], rect["y"])
        cdp.wait_for("document.body.innerText.includes('Circle complete')")
        record(4, "completed circle: three pots paid, collateral returned")
        time.sleep(6)
        for _ in range(3):
            cdp.wheel(720, 500, 240)
            time.sleep(0.5)
        time.sleep(2)

        # rules page from the actions section
        rect = link_rect(cdp, "Rules and guarantees")
        if rect:
            cdp.click(rect["x"], rect["y"])
            cdp.wait_for("document.body.innerText.includes('Fisher-Yates')")
            record(5, "rules: the payout order cannot be rigged")
            time.sleep(6)
            for _ in range(4):
                cdp.wheel(720, 500, 240)
                time.sleep(0.5)
            time.sleep(2)

    record(6, "end")
    with open("/tmp/kolektif_timeline.json", "w") as f:
        json.dump(TIMELINE, f, indent=2)
    print(json.dumps(TIMELINE, indent=2), flush=True)


if __name__ == "__main__":
    main()
