from pathlib import Path

p = Path("scenes/birthday_slides.py")
s = p.read_text(encoding="utf-8")

old = """        if not self.music_sync:
            duration = self.slides[self.index]["duration"]
            if self.elapsed >= duration:
                self.next_slide()
"""

new = """        duration = self.slides[self.index]["duration"]
        if self.elapsed >= duration:
            self.next_slide()
"""

if old not in s:
    print("ERROR: target block not found")
else:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    print("DONE - countdown timer fixed")