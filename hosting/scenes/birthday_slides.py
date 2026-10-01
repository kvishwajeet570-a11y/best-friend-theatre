import asyncio
import math
import random
from pathlib import Path

import pygame

from engine.effects import EffectsManager


class BirthdaySlides:
    """
    Premium cinematic birthday slideshow for Avantika.

    Slides:
        0  Countdown 3
        1  Countdown 2
        2  Countdown 1
        3  Happy Birthday Avantika
        4  Girl + Cake
        5  Make A Wish
        6  Celebration
        7  Memory / Photos
        8  A Little Message
        9  You Are...
        10 Many More Adventures
        11 Friendship Status
        12 Final Birthday
    """

    WIDTH = 1280
    HEIGHT = 720

    BG = (10, 8, 24)
    WHITE = (255, 255, 255)
    PINK = (255, 150, 205)
    LIGHT_PINK = (255, 215, 235)
    GOLD = (255, 220, 130)
    PURPLE = (180, 150, 255)

    def __init__(self, screen, audio=None):
        self.screen = screen
        self.audio = audio

        self.width, self.height = screen.get_size()

        self.root = Path(__file__).resolve().parent.parent
        self.image_dir = self.root / "assets" / "images"
        self.photo_dir = self.image_dir / "photos"

        self.clock = pygame.time.Clock()

        # ---------------------------------------------------------
        # Fonts
        # ---------------------------------------------------------
        self.font_big = pygame.font.SysFont(
            "segoeuisemibold", 86, bold=True
        )
        self.font_huge = pygame.font.SysFont(
            "segoeuisemibold", 170, bold=True
        )
        self.font_title = pygame.font.SysFont(
            "segoeuisemibold", 62, bold=True
        )
        self.font_subtitle = pygame.font.SysFont(
            "segoeui", 30
        )
        self.font_message = pygame.font.SysFont(
            "segoeui", 34
        )
        self.font_small = pygame.font.SysFont(
            "segoeui", 20
        )

        # ---------------------------------------------------------
        # Images
        # ---------------------------------------------------------
        self.images = {}

        self._load_image("girl_idle.png", "girl_idle", alpha=True)
        self._load_image("girl_happy.png", "girl_happy", alpha=True)
        self._load_image(
            "girl_celebrate.png",
            "girl_celebrate",
            alpha=True
        )
        self._load_image("cake.png", "cake", alpha=True)
        self._load_image(
            "friendship_card.png",
            "friendship_card",
            alpha=True,
        )

        self._load_image(
            "background_garden.png",
            "garden",
            alpha=False
        )
        self._load_image(
            "background_birthday.png",
            "birthday",
            alpha=False
        )
        self._load_image(
            "background_finale.png",
            "finale",
            alpha=False
        )

        # ---------------------------------------------------------
        # Photos
        # ---------------------------------------------------------
        self.photos = self._load_photos()

        # ---------------------------------------------------------
        # Slide configuration
        # ---------------------------------------------------------
        self.slides = [
            {"duration": 2.0, "kind": "countdown", "number": "3"},
            {"duration": 2.0, "kind": "countdown", "number": "2"},
            {"duration": 2.0, "kind": "countdown", "number": "1"},
            {"duration": 5.0, "kind": "birthday"},
            {"duration": 7.0, "kind": "girl_cake"},
            {"duration": 6.0, "kind": "wish"},
            {"duration": 6.0, "kind": "celebration"},
            {"duration": 7.0, "kind": "memory"},
            {"duration": 9.0, "kind": "message"},
            {"duration": 5.0, "kind": "you_are"},
            {"duration": 5.0, "kind": "adventure"},
            {"duration": 4.0, "kind": "friendship"},
            {"duration": 5.0, "kind": "finale"},
        ]

        self.index = 0
        self.elapsed = 0.0

        # The supplied birthday.mp3 is intended to drive the
        # complete 65-second visual timeline.
        self.music_sync = True
        self.music_sync_grace = 0.0

        self.running = False
        self.paused = False

        # ---------------------------------------------------------
        # Animation state
        # ---------------------------------------------------------
        self.total_time = 0.0
        self.transition = 0.0
        self.transitioning = False
        self.transition_direction = 1

        # Particles
        self.particles = []
        self.confetti = []

        # Floating stars
        self.stars = []
        self.sparkles = []

        for _ in range(100):
            self.stars.append(
                {
                    "x": random.uniform(0, self.width),
                    "y": random.uniform(0, self.height),
                    "r": random.uniform(0.5, 2.2),
                    "phase": random.uniform(0, math.tau),
                    "speed": random.uniform(0.7, 2.0),
                }
            )

        for _ in range(55):
            self.sparkles.append(
                {
                    "x": random.uniform(0, self.width),
                    "y": random.uniform(0, self.height),
                    "size": random.uniform(1.0, 3.2),
                    "phase": random.uniform(0, math.tau),
                    "speed": random.uniform(0.8, 2.2),
                }
            )

        self._create_confetti(80)

        # ---------------------------------------------------------
        # Cinematic Effects Engine
        # ---------------------------------------------------------
        self.effects = EffectsManager(
            self.width,
            self.height,
        )
        self._effects_slide_index = None

    # =============================================================
    # FILE / IMAGE HELPERS
    # =============================================================

    def _load_image(self, filename, key, alpha=True):
        path = self.image_dir / filename

        if not path.exists():
            print(f"[BirthdaySlides] Missing image: {path}")
            return

        try:
            image = pygame.image.load(str(path))

            if alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            self.images[key] = image
            print(f"[BirthdaySlides] Loaded: {filename}")

        except pygame.error as exc:
            print(
                f"[BirthdaySlides] Could not load "
                f"{filename}: {exc}"
            )

    def _load_photos(self):
        photos = []

        if not self.photo_dir.exists():
            return photos

        extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        }

        for path in sorted(self.photo_dir.iterdir()):
            if path.suffix.lower() not in extensions:
                continue

            try:
                image = pygame.image.load(str(path)).convert()
                photos.append(image)
            except pygame.error:
                pass

        print(
            f"[BirthdaySlides] Memory photos loaded: "
            f"{len(photos)}"
        )

        return photos

    @staticmethod
    def _pulse(time_value, speed=2.0):
        """Return a smooth 0..1 pulse value."""
        return (
            math.sin(time_value * speed) + 1.0
        ) / 2.0

    # =============================================================
    # BASIC DRAWING
    # =============================================================

    def _fill_gradient(self, top, bottom):
        for y in range(self.height):
            t = y / max(1, self.height - 1)

            color = (
                int(top[0] * (1 - t) + bottom[0] * t),
                int(top[1] * (1 - t) + bottom[1] * t),
                int(top[2] * (1 - t) + bottom[2] * t),
            )

            pygame.draw.line(
                self.screen,
                color,
                (0, y),
                (self.width, y),
            )

    def _draw_image_cover(self, image):
        if image is None:
            return

        iw, ih = image.get_size()

        scale = max(
            self.width / iw,
            self.height / ih,
        )

        nw = int(iw * scale)
        nh = int(ih * scale)

        resized = pygame.transform.smoothscale(
            image,
            (nw, nh),
        )

        x = (self.width - nw) // 2
        y = (self.height - nh) // 2

        self.screen.blit(resized, (x, y))

    def _draw_image_contain(
        self,
        image,
        rect,
        max_scale=1.0,
    ):
        if image is None:
            return

        iw, ih = image.get_size()

        scale = min(
            rect.width / iw,
            rect.height / ih,
            max_scale,
        )

        nw = max(1, int(iw * scale))
        nh = max(1, int(ih * scale))

        resized = pygame.transform.smoothscale(
            image,
            (nw, nh),
        )

        x = rect.centerx - nw // 2
        y = rect.centery - nh // 2

        self.screen.blit(resized, (x, y))

    def _center_text(
        self,
        text,
        font,
        color,
        y,
    ):
        surface = font.render(text, True, color)

        x = self.width // 2 - surface.get_width() // 2

        self.screen.blit(surface, (x, y))

    def _draw_glow_text(
        self,
        text,
        font,
        color,
        center,
        glow_color=None,
        glow_strength=1.0,
    ):
        """
        High-contrast cinematic text.
        Keeps text readable over bright image backgrounds.
        """
        if glow_color is None:
            glow_color = color

        base = font.render(text, True, color)

        cx = center[0] - base.get_width() // 2
        cy = center[1] - base.get_height() // 2

        # Dark shadow
        shadow = font.render(
            text,
            True,
            (0, 0, 0),
        )
        shadow.set_alpha(210)

        self.screen.blit(
            shadow,
            (cx + 5, cy + 6),
        )

        # Soft glow
        glow = font.render(
            text,
            True,
            glow_color,
        )

        for radius, alpha in [
            (12, 18),
            (8, 28),
            (5, 42),
            (2, 58),
        ]:
            layer = pygame.Surface(
                base.get_size(),
                pygame.SRCALPHA,
            )

            layer.blit(
                glow,
                (0, 0),
            )

            layer.set_alpha(
                int(alpha * glow_strength)
            )

            for dx, dy in [
                (-radius, 0),
                (radius, 0),
                (0, -radius),
                (0, radius),
                (-radius, -radius),
                (radius, -radius),
                (-radius, radius),
                (radius, radius),
            ]:
                self.screen.blit(
                    layer,
                    (
                        cx + dx,
                        cy + dy,
                    ),
                )

        # Dark outline
        outline = font.render(
            text,
            True,
            (32, 18, 42),
        )
        outline.set_alpha(230)

        for dx, dy in [
            (-2, 0),
            (2, 0),
            (0, -2),
            (0, 2),
            (-2, -2),
            (2, -2),
            (-2, 2),
            (2, 2),
        ]:
            self.screen.blit(
                outline,
                (
                    cx + dx,
                    cy + dy,
                ),
            )

        # Final text
        self.screen.blit(
            base,
            (cx, cy),
        )

    # =============================================================
    # PARTICLES
    # =============================================================

    def _create_confetti(self, count):
        colors = [
            self.PINK,
            self.GOLD,
            self.PURPLE,
            (150, 230, 255),
            (255, 255, 255),
        ]

        for _ in range(count):
            self.confetti.append(
                {
                    "x": random.uniform(0, self.width),
                    "y": random.uniform(-self.height, 0),
                    "vx": random.uniform(-0.8, 0.8),
                    "vy": random.uniform(1.5, 4.0),
                    "size": random.uniform(3, 8),
                    "phase": random.uniform(0, math.tau),
                    "color": random.choice(colors),
                }
            )

    def _update_confetti(self, dt):
        for p in self.confetti:
            p["x"] += p["vx"] * 60 * dt
            p["y"] += p["vy"] * 60 * dt
            p["phase"] += dt * 6

            if p["y"] > self.height + 20:
                p["y"] = random.uniform(-80, -10)
                p["x"] = random.uniform(
                    0,
                    self.width,
                )

    def _draw_confetti(self):
        for p in self.confetti:
            wobble = math.sin(p["phase"]) * 3

            rect = pygame.Rect(
                int(p["x"] + wobble),
                int(p["y"]),
                int(p["size"]),
                int(p["size"] * 1.7),
            )

            pygame.draw.rect(
                self.screen,
                p["color"],
                rect,
                border_radius=2,
            )

    def _draw_stars(self):
        for star in self.stars:
            alpha = int(
                90
                + 80
                * (
                    math.sin(
                        self.total_time
                        * star["speed"]
                        + star["phase"]
                    )
                    + 1
                )
                / 2
            )

            layer = pygame.Surface(
                (10, 10),
                pygame.SRCALPHA,
            )

            pygame.draw.circle(
                layer,
                (255, 255, 255, alpha),
                (5, 5),
                int(star["r"]),
            )

            self.screen.blit(
                layer,
                (
                    int(star["x"]),
                    int(star["y"]),
                ),
            )

    def _draw_sparkles(self):
        """Draw subtle animated sparkles over the scene."""
        for sparkle in self.sparkles:
            pulse = (
                math.sin(
                    self.total_time * sparkle["speed"]
                    + sparkle["phase"]
                )
                + 1.0
            ) / 2.0

            alpha = int(35 + pulse * 170)

            size = max(
                1,
                int(
                    sparkle["size"]
                    + pulse * 1.4
                ),
            )

            surface = pygame.Surface(
                (size * 6, size * 6),
                pygame.SRCALPHA,
            )

            cx = surface.get_width() // 2
            cy = surface.get_height() // 2

            pygame.draw.line(
                surface,
                (255, 255, 255, alpha),
                (cx - size * 2, cy),
                (cx + size * 2, cy),
                1,
            )

            pygame.draw.line(
                surface,
                (255, 255, 255, alpha),
                (cx, cy - size * 2),
                (cx, cy + size * 2),
                1,
            )

            pygame.draw.circle(
                surface,
                (
                    255,
                    220,
                    150,
                    min(255, alpha + 30),
                ),
                (cx, cy),
                max(1, size // 2),
            )

            self.screen.blit(
                surface,
                (
                    int(sparkle["x"] - cx),
                    int(sparkle["y"] - cy),
                ),
            )


    def _draw_heart(
        self,
        x,
        y,
        size,
        color,
        alpha=255,
    ):
        surface = pygame.Surface(
            (size * 2, size * 2),
            pygame.SRCALPHA,
        )

        points = []

        for i in range(101):
            t = math.tau * i / 100

            hx = (
                16 * math.sin(t) ** 3
            )

            hy = -(
                13 * math.cos(t)
                - 5 * math.cos(2 * t)
                - 2 * math.cos(3 * t)
                - math.cos(4 * t)
            )

            px = size + hx * size / 34
            py = size + hy * size / 34

            points.append((px, py))

        pygame.draw.polygon(
            surface,
            (*color, alpha),
            points,
        )

        self.screen.blit(
            surface,
            (
                int(x - size),
                int(y - size),
            ),
        )

    # =============================================================
    # BACKGROUND
    # =============================================================
    def _draw_vignette(self, strength=0.45):
        """Add a subtle cinematic edge-darkening vignette."""
        strength = max(0.0, min(1.0, float(strength)))

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        edge = int(90 * strength)
        side = int(55 * strength)

        pygame.draw.rect(
            overlay,
            (0, 0, 0, edge),
            (0, 0, self.width, 75),
        )

        pygame.draw.rect(
            overlay,
            (0, 0, 0, edge),
            (0, self.height - 85, self.width, 85),
        )

        pygame.draw.rect(
            overlay,
            (0, 0, 0, side),
            (0, 0, 55, self.height),
        )

        pygame.draw.rect(
            overlay,
            (0, 0, 0, side),
            (self.width - 55, 0, 55, self.height),
        )

        self.screen.blit(overlay, (0, 0))


    def _draw_background(self, name):
        image = self.images.get(name)

        if image:
            self._draw_image_cover(image)
        else:
            self._fill_gradient(
                (14, 8, 35),
                (55, 20, 65),
            )

    # =============================================================
    # SLIDE DRAWING
    # =============================================================

    def _draw_countdown(self, number):
        self._fill_gradient(
            (8, 7, 25),
            (43, 13, 63),
        )

        self._draw_stars()

        pulse = (
            math.sin(self.total_time * 4)
            + 1
        ) / 2

        radius = int(
            120
            + pulse * 28
        )

        for r, alpha in [
            (radius + 30, 35),
            (radius + 15, 60),
            (radius, 100),
        ]:
            ring = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA,
            )

            pygame.draw.circle(
                ring,
                (*self.PINK, alpha),
                (
                    self.width // 2,
                    self.height // 2,
                ),
                r,
                3,
            )

            self.screen.blit(
                ring,
                (0, 0),
            )

        self._draw_glow_text(
            number,
            self.font_huge,
            self.WHITE,
            (
                self.width // 2,
                self.height // 2,
            ),
            self.PINK,
        )

        self._center_text(
            "Something special is coming...",
            self.font_subtitle,
            self.LIGHT_PINK,
            self.height // 2 + 130,
        )

    def _draw_birthday(self):
        self._draw_background("birthday")

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill((8, 4, 20, 65))

        self.screen.blit(
            overlay,
            (0, 0),
        )

        self._draw_stars()

        self._draw_glow_text(
            "HAPPY BIRTHDAY",
            self.font_title,
            self.WHITE,
            (self.width // 2, 170),
            self.PINK,
        )

        self._draw_glow_text(
            "Avantika",
            self.font_big,
            self.GOLD,
            (self.width // 2, 250),
            self.GOLD,
        )

        # Animated hearts
        for i in range(7):
            angle = (
                self.total_time * 0.5
                + i * math.tau / 7
            )

            x = (
                self.width // 2
                + math.cos(angle) * 350
            )

            y = (
                220
                + math.sin(angle) * 100
            )

            self._draw_heart(
                x,
                y,
                12 + (i % 3) * 4,
                self.PINK,
                190,
            )

        self._center_text(
            "Today is all about your smile ✨",
            self.font_subtitle,
            self.LIGHT_PINK,
            350,
        )

    def _draw_girl_cake(self):
        self._draw_background("garden")

        # Dark cinematic overlay
        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill((5, 3, 18, 72))

        self.screen.blit(
            overlay,
            (0, 0),
        )

        girl = self.images.get("girl_happy")
        cake = self.images.get("cake")

        # Girl
        if girl:
            scale = (
                0.48
                + 0.025
                * math.sin(self.total_time * 2)
            )

            rect = pygame.Rect(
                500,
                120,
                470,
                570,
            )

            self._draw_image_contain(
                girl,
                rect,
                scale,
            )

        # Cake
        if cake:
            rect = pygame.Rect(
                70,
                400,
                390,
                270,
            )

            self._draw_image_contain(
                cake,
                rect,
                0.8,
            )

        self._draw_glow_text(
            "HAPPY BIRTHDAY Avantika",
            self.font_title,
            self.WHITE,
            (self.width // 2, 70),
            self.PINK,
        )

    def _draw_wish(self):
        self._draw_background("garden")

        dark = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        dark.fill((8, 5, 25, 95))

        self.screen.blit(
            dark,
            (0, 0),
        )

        cake = self.images.get("cake")

        if cake:
            rect = pygame.Rect(
                390,
                260,
                500,
                360,
            )

            self._draw_image_contain(
                cake,
                rect,
                0.95,
            )

        # Candle-like glow
        pulse = (
            math.sin(self.total_time * 6)
            + 1
        ) / 2

        pygame.draw.circle(
            self.screen,
            (255, 180, 90),
            (640, 250),
            int(18 + pulse * 8),
        )

        self._draw_glow_text(
            "MAKE A WISH",
            self.font_title,
            self.WHITE,
            (self.width // 2, 120),
            self.GOLD,
        )

        self._center_text(
            "Close your eyes... make it a good one ✨",
            self.font_subtitle,
            self.LIGHT_PINK,
            650,
        )

    def _draw_celebration(self):
        self._draw_background("birthday")

        # Soft cinematic darkening for readability without
        # killing the colors of the background.
        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )
        overlay.fill((8, 4, 22, 42))
        self.screen.blit(overlay, (0, 0))

        self._draw_confetti()
        self._draw_sparkles()

        # -----------------------------------------------------
        # EXACT uploaded celebration artwork
        # -----------------------------------------------------
        girl = self.images.get("girl_celebrate")

        if girl:
            float_y = math.sin(
                self.total_time * 1.8
            ) * 7

            pulse = (
                1.0
                + 0.018
                * math.sin(self.total_time * 2.2)
            )

            rect = pygame.Rect(
                45,
                125,
                590,
                560,
            )

            # Gentle glow behind the artwork
            glow = pygame.Surface(
                (640, 640),
                pygame.SRCALPHA,
            )

            glow_alpha = int(
                18
                + self._pulse(self.total_time, 2.5) * 18
            )

            pygame.draw.circle(
                glow,
                (
                    255,
                    150,
                    205,
                    glow_alpha,
                ),
                (320, 315),
                250,
            )

            self.screen.blit(
                glow,
                (15, 75),
            )

            # Draw the transparent PNG without a white box.
            self._draw_image_contain(
                girl,
                pygame.Rect(
                    rect.x,
                    int(rect.y + float_y),
                    rect.width,
                    rect.height,
                ),
                pulse,
            )

        # -----------------------------------------------------
        # Celebration text panel
        # -----------------------------------------------------

        panel = pygame.Surface(
            (560, 500),
            pygame.SRCALPHA,
        )

        panel.fill(
            (13, 7, 32, 92)
        )

        pygame.draw.rect(
            panel,
            (255, 150, 205, 105),
            panel.get_rect(),
            2,
            border_radius=28,
        )

        pygame.draw.line(
            panel,
            (255, 220, 130, 115),
            (45, 92),
            (515, 92),
            2,
        )

        self.screen.blit(
            panel,
            (650, 120),
        )

        self._draw_glow_text(
            "YAY! 🎉",
            self.font_big,
            self.WHITE,
            (930, 210),
            self.PINK,
            1.0,
        )

        self._draw_glow_text(
            "IT'S YOUR DAY!",
            self.font_title,
            self.GOLD,
            (930, 300),
            self.GOLD,
            0.85,
        )

        self._center_text(
            "Keep smiling always.",
            self.font_subtitle,
            self.LIGHT_PINK,
            390,
        )

        self._center_text(
            "More laughs • more memories",
            self.font_small,
            self.WHITE,
            440,
        )

        self._center_text(
            "• more reasons to celebrate •",
            self.font_small,
            self.PINK,
            475,
        )

        self._draw_heart(
            930,
            545,
            24,
            self.PINK,
            205,
        )

        self._center_text(
            "Made especially for Avantika ✨",
            self.font_small,
            self.LIGHT_PINK,
            610,
        )

        self._draw_vignette(0.32)

    def _draw_memory(self):

        self._draw_background("garden")

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        # Keep the background visible and colourful.
        overlay.fill(
            (8, 5, 22, 55)
        )

        self.screen.blit(
            overlay,
            (0, 0),
        )

        self._draw_sparkles()

        self._draw_glow_text(
            "SOME MOMENTS",
            self.font_title,
            self.WHITE,
            (self.width // 2, 70),
            self.PINK,
        )

        self._center_text(
            "THAT MEAN EVERYTHING",
            self.font_subtitle,
            self.GOLD,
            125,
        )

        # -----------------------------------------------------
        # FRIENDSHIP CARD ONLY
        # -----------------------------------------------------
        card = self.images.get(
            "friendship_card"
        )

        if card is not None:

            float_y = math.sin(
                self.total_time * 1.25
            ) * 5

            pulse = (
                1.0
                + 0.012
                * math.sin(
                    self.total_time * 2.0
                )
            )

            card_rect = pygame.Rect(
                250,
                170,
                780,
                500,
            )

            # Premium shadow
            shadow = pygame.Surface(
                (
                    card_rect.width + 36,
                    card_rect.height + 36,
                ),
                pygame.SRCALPHA,
            )

            pygame.draw.rect(
                shadow,
                (0, 0, 0, 115),
                shadow.get_rect(),
                border_radius=26,
            )

            self.screen.blit(
                shadow,
                (
                    card_rect.x - 18,
                    int(card_rect.y + float_y + 16),
                ),
            )

            # Soft outer glow
            glow = pygame.Surface(
                (
                    card_rect.width + 50,
                    card_rect.height + 50,
                ),
                pygame.SRCALPHA,
            )

            pygame.draw.rect(
                glow,
                (255, 150, 205, 22),
                glow.get_rect(),
                border_radius=30,
            )

            self.screen.blit(
                glow,
                (
                    card_rect.x - 25,
                    int(card_rect.y + float_y - 8),
                ),
            )

            # Gentle breathing animation
            draw_width = int(
                card_rect.width * pulse
            )

            draw_height = int(
                card_rect.height * pulse
            )

            draw_rect = pygame.Rect(
                0,
                0,
                draw_width,
                draw_height,
            )

            draw_rect.center = (
                card_rect.centerx,
                int(
                    card_rect.centery
                    + float_y
                ),
            )

            self._draw_image_contain(
                card,
                draw_rect,
                1.0,
            )

        else:
            # Do not show a placeholder card.
            # Just keep the scene clean if the asset is absent.
            self._center_text(
                " ",
                self.font_small,
                self.WHITE,
                self.height - 30,
            )

        self._draw_vignette(
            0.32
        )

    def _draw_message(self):
        self._draw_background("garden")

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill((5, 3, 18, 125))

        self.screen.blit(
            overlay,
            (0, 0),
        )

        self._draw_glow_text(
            "A LITTLE MESSAGE",
            self.font_title,
            self.WHITE,
            (self.width // 2, 105),
            self.PINK,
        )

        lines = [
            "Some people enter our lives",
            "and quietly make ordinary days",
            "feel a little more special.",
            "",
            "Thank you for all the laughs,",
            "the crazy moments,",
            "and the memories we've made.",
            "",
            "Stay happy. Stay awesome.",
            "And keep being YOU. ✨",
        ]

        start_y = 190

        for i, line in enumerate(lines):
            alpha = min(
                255,
                int(
                    max(
                        0,
                        self.elapsed - i * 0.35,
                    )
                    * 400
                ),
            )

            if alpha <= 0:
                continue

            surface = self.font_message.render(
                line,
                True,
                self.LIGHT_PINK,
            )

            surface.set_alpha(alpha)

            self.screen.blit(
                surface,
                (
                    self.width // 2
                    - surface.get_width() // 2,
                    start_y + i * 42,
                ),
            )

    def _draw_you_are(self):
        self._fill_gradient(
            (15, 8, 35),
            (70, 18, 65),
        )

        self._draw_stars()

        self._draw_glow_text(
            "YOU ARE...",
            self.font_title,
            self.WHITE,
            (self.width // 2, 120),
            self.PINK,
        )

        words = [
            "Kind",
            "Crazy",
            "Funny",
            "Supportive",
            "Unforgettable",
        ]

        positions = [
            (350, 260),
            (640, 220),
            (930, 260),
            (470, 430),
            (800, 430),
        ]

        for i, word in enumerate(words):
            x, y = positions[i]

            float_y = (
                math.sin(
                    self.total_time * 2
                    + i
                )
                * 12
            )

            self._draw_glow_text(
                word,
                self.font_title,
                self.WHITE,
                (
                    x,
                    int(y + float_y),
                ),
                self.PINK if i % 2 == 0 else self.GOLD,
            )

    def _draw_adventure(self):
        self._draw_background("birthday")

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill((5, 5, 25, 62))

        self.screen.blit(
            overlay,
            (0, 0),
        )

        self._draw_glow_text(
            "HERE'S TO",
            self.font_title,
            self.WHITE,
            (self.width // 2, 140),
            self.PINK,
        )

        self._draw_glow_text(
            "MANY MORE ADVENTURES",
            self.font_title,
            self.GOLD,
            (self.width // 2, 220),
            self.GOLD,
        )

        cards = [
            "More laughs",
            "More crazy stories",
            "More memories",
            "More celebrations",
        ]

        for i, text in enumerate(cards):
            x = 170 + i * 305

            rect = pygame.Rect(
                x,
                350,
                250,
                130,
            )

            surface = pygame.Surface(
                rect.size,
                pygame.SRCALPHA,
            )

            surface.fill(
                (255, 180, 220, 35)
            )

            pygame.draw.rect(
                surface,
                (*self.PINK, 100),
                surface.get_rect(),
                2,
                border_radius=18,
            )

            self.screen.blit(
                surface,
                rect.topleft,
            )

            txt = self.font_small.render(
                text,
                True,
                self.WHITE,
            )

            self.screen.blit(
                txt,
                (
                    rect.centerx
                    - txt.get_width() // 2,
                    rect.centery
                    - txt.get_height() // 2,
                ),
            )

    def _draw_friendship(self):
        self._draw_background("garden")

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill((8, 4, 25, 72))

        self.screen.blit(
            overlay,
            (0, 0),
        )

        self._draw_glow_text(
            "FRIENDSHIP STATUS",
            self.font_title,
            self.WHITE,
            (self.width // 2, 140),
            self.PINK,
        )

        self._draw_glow_text(
            "ACTIVE ✓",
            self.font_huge,
            self.GOLD,
            (self.width // 2, 280),
            self.GOLD,
        )

        points = [
            "Same crazy",
            "Same silly",
            "Same supportive",
            "Same forever",
        ]

        for i, text in enumerate(points):
            x = self.width // 2
            y = 410 + i * 48

            self._center_text(
                text,
                self.font_subtitle,
                self.LIGHT_PINK,
                y,
            )

    def _draw_finale(self):
        self._draw_background("finale")

        # Dark vignette
        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA,
        )

        overlay.fill((4, 3, 20, 28))

        self.screen.blit(
            overlay,
            (0, 0),
        )

        self._draw_confetti()

        # Floating hearts
        for i in range(12):
            angle = (
                self.total_time * 0.35
                + i * math.tau / 12
            )

            x = (
                self.width // 2
                + math.cos(angle) * 470
            )

            y = (
                340
                + math.sin(angle) * 210
            )

            self._draw_heart(
                x,
                y,
                10 + i % 4 * 3,
                self.PINK,
                170,
            )

        self._draw_glow_text(
            "HAPPY BIRTHDAY",
            self.font_title,
            self.WHITE,
            (self.width // 2, 260),
            self.GOLD,
        )

        self._draw_glow_text(
            "Avantika",
            self.font_huge,
            self.PINK,
            (self.width // 2, 380),
            self.PINK,
        )

        self._center_text(
            "Keep smiling. Keep shining. Keep being amazing. ✨",
            self.font_subtitle,
            self.LIGHT_PINK,
            500,
        )

        self._center_text(
            "— Your Best Friend Theatre 🎬",
            self.font_small,
            self.WHITE,
            590,
        )

    # =============================================================
    # CINEMATIC EFFECTS
    # =============================================================

    def _trigger_effects_for_slide(self, force=False):
        """Trigger one-shot cinematic effects when a slide is entered."""
        if not force and self._effects_slide_index == self.index:
            return

        self._effects_slide_index = self.index
        kind = self.slides[self.index]["kind"]

        try:
            self.effects.clear()

            if kind == "birthday":
                self.effects.birthday_burst()
            elif kind == "girl_cake":
                self.effects.set_flame_active(True)
                self.effects.birthday_burst()
            elif kind == "wish":
                self.effects.set_flame_active(True)
            elif kind == "celebration":
                self.effects.set_flame_active(False)
                self.effects.celebration_burst()
            elif kind == "finale":
                self.effects.set_flame_active(False)
                self.effects.finale_burst()
            else:
                self.effects.set_flame_active(False)
        except Exception as exc:
            print(f"[BirthdaySlides] Effects warning: {exc}")

    def _update_effects(self, dt):
        try:
            self.effects.update(dt)
        except Exception as exc:
            print(f"[BirthdaySlides] Effects update warning: {exc}")

    def _draw_effect_overlay(self):
        try:
            self.effects.draw_overlay(self.screen)
        except Exception as exc:
            print(f"[BirthdaySlides] Effects draw warning: {exc}")

    # =============================================================
    # SLIDE ROUTER
    # =============================================================

    def draw_current_slide(self):
        slide = self.slides[self.index]
        kind = slide["kind"]

        if kind == "countdown":
            self._draw_countdown(
                slide["number"]
            )

        elif kind == "birthday":
            self._draw_birthday()

        elif kind == "girl_cake":
            self._draw_girl_cake()

        elif kind == "wish":
            self._draw_wish()

        elif kind == "celebration":
            self._draw_celebration()

        elif kind == "memory":
            self._draw_memory()

        elif kind == "message":
            self._draw_message()

        elif kind == "you_are":
            self._draw_you_are()

        elif kind == "adventure":
            self._draw_adventure()

        elif kind == "friendship":
            self._draw_friendship()

        elif kind == "finale":
            self._draw_finale()

        self._draw_effect_overlay()

    # =============================================================
    # NAVIGATION
    # =============================================================

    def next_slide(self):
        if self.index < len(self.slides) - 1:
            self.index += 1
            self.elapsed = 0.0
            self.music_sync_grace = 1.25
            self._trigger_effects_for_slide(force=True)
        else:
            self.running = False

    def previous_slide(self):
        self.index = max(0, self.index - 1)
        self.elapsed = 0.0
        self.music_sync_grace = 0.6
        self._trigger_effects_for_slide(force=True)

    def _music_timeline_index(self, position):
        elapsed = 0.0

        for i, slide in enumerate(self.slides):
            elapsed += slide["duration"]

            if position < elapsed:
                return i

        return len(self.slides) - 1

    def _sync_to_music(self):
        if not self.music_sync or self.audio is None:
            return

        if not hasattr(self.audio, "music_position"):
            return

        if self.music_sync_grace > 0.0:
            return

        try:
            current_music = str(
                getattr(self.audio, "current_music", "")
            ).lower()

            if current_music not in {"birthday.mp3", "birthday.ogg"}:
                return

            position = self.audio.music_position()
            target = self._music_timeline_index(position)

            if target != self.index:
                self.index = target
                self.elapsed = 0.0
                self._trigger_effects_for_slide(force=True)

            start_time = sum(
                self.slides[i]["duration"]
                for i in range(self.index)
            )
            self.elapsed = max(0.0, position - start_time)

        except Exception as exc:
            print(f"[BirthdaySlides] Music sync warning: {exc}")
            self.music_sync = False

    # =============================================================
    # UPDATE
    # =============================================================

    def update(self, dt):
        if self.paused:
            return

        self.total_time += dt
        self.elapsed += dt

        if self.music_sync_grace > 0.0:
            self.music_sync_grace = max(
                0.0,
                self.music_sync_grace - dt,
            )

        self._update_confetti(dt)
        self._update_effects(dt)
        self._trigger_effects_for_slide()
        self._sync_to_music()

        if not self.music_sync:
            duration = self.slides[self.index]["duration"]
            if self.elapsed >= duration:
                self.next_slide()

    # =============================================================
    # EVENT HANDLING
    # =============================================================

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RIGHT:
                self.next_slide()

            elif event.key == pygame.K_LEFT:
                self.previous_slide()

            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused

            elif event.key == pygame.K_ESCAPE:
                self.running = False

            elif event.key == pygame.K_HOME:
                self.index = 0
                self.elapsed = 0
                self._trigger_effects_for_slide(force=True)

            elif event.key == pygame.K_END:
                self.index = len(self.slides) - 1
                self.elapsed = 0
                self._trigger_effects_for_slide(force=True)

    # =============================================================
    # MAIN LOOP
    # =============================================================

    def run(self):
        self.running = True
        self._trigger_effects_for_slide(force=True)

        while self.running:

            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                self.handle_event(event)

            self.update(dt)

            self.draw_current_slide()

            pygame.display.flip()

        return True


    async def run_web(self):
        """
        Pygbag/browser-compatible asynchronous main loop.

        Every frame yields control back to the browser with
        asyncio.sleep(0), preventing the page from becoming
        unresponsive while keeping the existing slideshow,
        music sync, and cinematic effects intact.
        """

        self.running = True
        self._trigger_effects_for_slide(force=True)

        while self.running:

            for event in pygame.event.get():
                self.handle_event(event)

            dt = self.clock.tick(60) / 1000.0

            # Guard against browser tab stalls / frame spikes.
            dt = max(0.0, min(dt, 0.05))

            self.update(dt)

            self.draw_current_slide()

            pygame.display.flip()

            # Critical for Pygbag/Emscripten.
            await asyncio.sleep(0)

        return True


    def draw(self):
        self.draw_current_slide()


# =================================================================
# STANDALONE TEST
# =================================================================

if __name__ == "__main__":

    pygame.init()

    screen = pygame.display.set_mode(
        (
            BirthdaySlides.WIDTH,
            BirthdaySlides.HEIGHT,
        )
    )

    pygame.display.set_caption(
        "Best Friend Theatre — Avantika"
    )

    show = BirthdaySlides(screen)

    show.run()

    pygame.quit()
