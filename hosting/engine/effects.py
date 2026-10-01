import math
import random

import pygame


# ============================================================
# BASIC HELPERS
# ============================================================

def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def lerp(a, b, t):
    t = clamp(t)
    return a + (b - a) * t


# ============================================================
# GLOW
# ============================================================

class Glow:
    """Utility for soft additive-style glow effects."""

    @staticmethod
    def circle(
        surface,
        center,
        radius,
        color=(255, 180, 220),
        alpha=100,
        layers=5,
    ):
        if radius <= 0:
            return

        width = max(
            32,
            int(radius * 2.8),
        )

        glow = pygame.Surface(
            (width, width),
            pygame.SRCALPHA,
        )

        cx = width // 2
        cy = width // 2

        layers = max(1, int(layers))

        for i in range(layers, 0, -1):

            ratio = i / layers

            current_radius = max(
                1,
                int(radius * ratio),
            )

            current_alpha = int(
                alpha
                * (1.0 - ratio * 0.72)
            )

            pygame.draw.circle(
                glow,
                (
                    color[0],
                    color[1],
                    color[2],
                    current_alpha,
                ),
                (cx, cy),
                current_radius,
            )

        surface.blit(
            glow,
            (
                int(center[0] - cx),
                int(center[1] - cy),
            ),
        )


# ============================================================
# SCREEN FLASH
# ============================================================

class ScreenFlash:
    """Full-screen flash that fades automatically."""

    def __init__(
        self,
        width,
        height,
    ):
        self.width = width
        self.height = height

        self.alpha = 0.0
        self.duration = 0.30
        self.timer = 0.0
        self.color = (255, 255, 255)

    def trigger(
        self,
        color=(255, 255, 255),
        strength=220,
        duration=0.30,
    ):
        self.color = color
        self.alpha = float(
            clamp(strength / 255.0)
        )
        self.duration = max(
            0.05,
            duration,
        )
        self.timer = 0.0

    def update(self, dt):

        if self.alpha <= 0:
            return

        self.timer += dt

        progress = clamp(
            self.timer
            / self.duration
        )

        self.alpha = (
            1.0 - progress
        )

        if progress >= 1.0:
            self.alpha = 0.0

    def draw(self, surface):

        if self.alpha <= 0:
            return

        overlay = pygame.Surface(
            (
                self.width,
                self.height,
            ),
            pygame.SRCALPHA,
        )

        overlay.fill(
            (
                self.color[0],
                self.color[1],
                self.color[2],
                int(
                    255
                    * self.alpha
                ),
            )
        )

        surface.blit(
            overlay,
            (0, 0),
        )


# ============================================================
# SCREEN SHAKE
# ============================================================

class ScreenShake:
    """Short cinematic camera shake."""

    def __init__(self):
        self.timer = 0.0
        self.duration = 0.0
        self.strength = 0.0

    def trigger(
        self,
        strength=8.0,
        duration=0.25,
    ):
        self.strength = max(
            self.strength,
            float(strength),
        )

        self.duration = max(
            self.duration,
            float(duration),
        )

        self.timer = self.duration

    def update(self, dt):

        if self.timer <= 0:
            return

        self.timer -= dt

        if self.timer <= 0:
            self.timer = 0.0
            self.strength = 0.0

    def offset(self):

        if self.timer <= 0:
            return (0, 0)

        ratio = clamp(
            self.timer
            / max(0.01, self.duration)
        )

        current = (
            self.strength
            * ratio
        )

        return (
            int(
                random.uniform(
                    -current,
                    current,
                )
            ),
            int(
                random.uniform(
                    -current,
                    current,
                )
            ),
        )


# ============================================================
# HEART
# ============================================================

class Heart:

    def __init__(
        self,
        x,
        y,
        size=16,
        color=(255, 150, 205),
        life=2.0,
        vx=0.0,
        vy=-25.0,
    ):
        self.x = float(x)
        self.y = float(y)

        self.size = float(size)

        self.color = color

        self.life = float(life)
        self.max_life = max(
            0.01,
            float(life),
        )

        self.vx = float(vx)
        self.vy = float(vy)

        self.phase = random.uniform(
            0,
            math.tau,
        )

        self.rotation = random.uniform(
            -10,
            10,
        )

    def update(self, dt):

        self.x += self.vx * dt

        self.y += self.vy * dt

        self.vy -= 5.0 * dt

        self.phase += dt * 3

        self.life -= dt

    def draw(self, surface):

        if self.life <= 0:
            return

        life_ratio = clamp(
            self.life
            / self.max_life
        )

        alpha = int(
            255
            * life_ratio
        )

        wobble = (
            math.sin(self.phase)
            * 3
        )

        size = max(
            3,
            int(
                self.size
                * (
                    0.85
                    + life_ratio * 0.15
                )
            ),
        )

        layer = pygame.Surface(
            (
                size * 2,
                size * 2,
            ),
            pygame.SRCALPHA,
        )

        points = []

        for i in range(101):

            t = (
                math.tau
                * i
                / 100
            )

            hx = (
                16
                * math.sin(t) ** 3
            )

            hy = -(
                13 * math.cos(t)
                - 5 * math.cos(2 * t)
                - 2 * math.cos(3 * t)
                - math.cos(4 * t)
            )

            px = (
                size
                + hx
                * size
                / 34
            )

            py = (
                size
                + hy
                * size
                / 34
            )

            points.append(
                (px, py)
            )

        pygame.draw.polygon(
            layer,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha,
            ),
            points,
        )

        surface.blit(
            layer,
            (
                int(
                    self.x
                    - size
                    + wobble
                ),
                int(
                    self.y
                    - size
                ),
            ),
        )

    @property
    def alive(self):
        return self.life > 0


# ============================================================
# HEART SYSTEM
# ============================================================

class HeartSystem:

    def __init__(self):
        self.hearts = []

    def burst(
        self,
        x,
        y,
        count=12,
        color=(255, 150, 205),
    ):
        for _ in range(count):

            angle = random.uniform(
                -math.pi * 0.85,
                -math.pi * 0.15,
            )

            speed = random.uniform(
                20,
                75,
            )

            self.hearts.append(
                Heart(
                    x,
                    y,
                    size=random.uniform(
                        8,
                        18,
                    ),
                    color=color,
                    life=random.uniform(
                        1.4,
                        2.4,
                    ),
                    vx=math.cos(angle)
                    * speed,
                    vy=math.sin(angle)
                    * speed,
                )
            )

    def update(self, dt):

        for heart in self.hearts:
            heart.update(dt)

        self.hearts = [
            heart
            for heart in self.hearts
            if heart.alive
        ]

    def draw(self, surface):

        for heart in self.hearts:
            heart.draw(surface)

    def clear(self):
        self.hearts.clear()


def draw_heart(
    surface,
    x,
    y,
    size,
    color,
    alpha=255,
):
    heart = Heart(
        x,
        y,
        size=size,
        color=color,
        life=1,
        vx=0,
        vy=0,
    )

    heart.life = 1

    heart.draw(surface)


# ============================================================
# CANDLE FLAME
# ============================================================

class CandleFlame:

    def __init__(
        self,
        x,
        y,
    ):
        self.x = float(x)
        self.y = float(y)

        self.phase = random.uniform(
            0,
            math.tau,
        )

    def update(self, dt):
        self.phase += dt * 8.0

    def draw(self, surface):

        pulse = (
            math.sin(self.phase)
            + 1.0
        ) / 2.0

        width = int(
            36
            + pulse * 10
        )

        height = int(
            60
            + pulse * 14
        )

        flame = pygame.Surface(
            (
                width,
                height,
            ),
            pygame.SRCALPHA,
        )

        cx = width // 2

        points = [
            (
                cx,
                3,
            ),
            (
                int(
                    width * 0.78
                ),
                int(
                    height * 0.42
                ),
            ),
            (
                cx,
                height - 2,
            ),
            (
                int(
                    width * 0.22
                ),
                int(
                    height * 0.42
                ),
            ),
        ]

        pygame.draw.polygon(
            flame,
            (255, 180, 80, 190),
            points,
        )

        inner = [
            (
                cx,
                int(height * 0.16),
            ),
            (
                int(
                    width * 0.66
                ),
                int(
                    height * 0.52
                ),
            ),
            (
                cx,
                int(
                    height * 0.82
                ),
            ),
            (
                int(
                    width * 0.34
                ),
                int(
                    height * 0.52
                ),
            ),
        ]

        pygame.draw.polygon(
            flame,
            (255, 240, 175, 230),
            inner,
        )

        surface.blit(
            flame,
            (
                int(
                    self.x
                    - width / 2
                ),
                int(
                    self.y
                    - height
                ),
            ),
        )


# ============================================================
# MAGIC AURA
# ============================================================

class MagicAura:

    def __init__(
        self,
        width,
        height,
    ):
        self.width = width
        self.height = height

        self.time = 0.0

    def update(self, dt):
        self.time += dt

    def draw(
        self,
        surface,
        center=None,
        color=(255, 150, 205),
        radius=160,
    ):
        if center is None:
            center = (
                self.width // 2,
                self.height // 2,
            )

        pulse = (
            math.sin(
                self.time * 2.0
            )
            + 1.0
        ) / 2.0

        for i in range(4):

            current_radius = int(
                radius
                + i * 28
                + pulse * 14
            )

            alpha = int(
                15
                + (
                    35
                    - i * 7
                )
                * pulse
            )

            Glow.circle(
                surface,
                center,
                current_radius,
                color,
                alpha,
                layers=3,
            )


# ============================================================
# CONFETTI PIECE
# ============================================================

class ConfettiPiece:

    def __init__(
        self,
        x,
        y,
        color,
        size=7,
    ):
        self.x = float(x)
        self.y = float(y)

        self.vx = random.uniform(
            -70,
            70,
        )

        self.vy = random.uniform(
            -160,
            -45,
        )

        self.gravity = random.uniform(
            90,
            180,
        )

        self.size = float(size)

        self.color = color

        self.life = random.uniform(
            1.5,
            3.0,
        )

        self.max_life = self.life

        self.rotation = random.uniform(
            0,
            math.tau,
        )

        self.rotation_speed = random.uniform(
            -7,
            7,
        )

        self.phase = random.uniform(
            0,
            math.tau,
        )

    def update(self, dt):

        self.x += self.vx * dt

        self.y += self.vy * dt

        self.vy += (
            self.gravity * dt
        )

        self.rotation += (
            self.rotation_speed
            * dt
        )

        self.phase += dt * 5

        self.life -= dt

    def draw(self, surface):

        if self.life <= 0:
            return

        alpha = int(
            255
            * clamp(
                self.life
                / self.max_life
            )
        )

        width = max(
            3,
            int(self.size),
        )

        height = max(
            4,
            int(
                self.size * 1.8
            ),
        )

        piece = pygame.Surface(
            (
                width * 4,
                height * 4,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            piece,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha,
            ),
            (
                width,
                height,
                width * 2,
                height * 2,
            ),
            border_radius=2,
        )

        piece = pygame.transform.rotate(
            piece,
            math.degrees(
                self.rotation
            ),
        )

        surface.blit(
            piece,
            (
                int(
                    self.x
                    - piece.get_width()
                    / 2
                ),
                int(
                    self.y
                    - piece.get_height()
                    / 2
                ),
            ),
        )

    @property
    def alive(self):
        return self.life > 0


# ============================================================
# CONFETTI SYSTEM
# ============================================================

class ConfettiSystem:

    COLORS = [
        (255, 150, 205),
        (255, 220, 130),
        (180, 150, 255),
        (150, 230, 255),
        (255, 255, 255),
    ]

    def __init__(self):
        self.pieces = []

    def burst(
        self,
        x,
        y,
        count=80,
    ):
        for _ in range(count):

            self.pieces.append(
                ConfettiPiece(
                    x
                    + random.uniform(
                        -50,
                        50,
                    ),
                    y
                    + random.uniform(
                        -25,
                        25,
                    ),
                    random.choice(
                        self.COLORS
                    ),
                    random.uniform(
                        4,
                        9,
                    ),
                )
            )

    def rain(
        self,
        width,
        height,
        count=60,
    ):
        for _ in range(count):

            self.pieces.append(
                ConfettiPiece(
                    random.uniform(
                        0,
                        width,
                    ),
                    random.uniform(
                        -height,
                        0,
                    ),
                    random.choice(
                        self.COLORS
                    ),
                    random.uniform(
                        3,
                        8,
                    ),
                )
            )

    def update(self, dt):

        for piece in self.pieces:
            piece.update(dt)

        self.pieces = [
            piece
            for piece in self.pieces
            if piece.alive
        ]

    def draw(self, surface):

        for piece in self.pieces:
            piece.draw(surface)

    def clear(self):
        self.pieces.clear()


# ============================================================
# STAR BURST
# ============================================================

def draw_star_burst(
    surface,
    center,
    radius=80,
    color=(255, 220, 130),
    rays=16,
    alpha=180,
):
    cx, cy = center

    burst = pygame.Surface(
        surface.get_size(),
        pygame.SRCALPHA,
    )

    for i in range(rays):

        angle = (
            i
            * math.tau
            / rays
        )

        inner = radius * 0.32
        outer = radius

        x1 = (
            cx
            + math.cos(angle)
            * inner
        )

        y1 = (
            cy
            + math.sin(angle)
            * inner
        )

        x2 = (
            cx
            + math.cos(angle)
            * outer
        )

        y2 = (
            cy
            + math.sin(angle)
            * outer
        )

        pygame.draw.line(
            burst,
            (
                color[0],
                color[1],
                color[2],
                alpha,
            ),
            (x1, y1),
            (x2, y2),
            2,
        )

    surface.blit(
        burst,
        (0, 0),
    )


# ============================================================
# FIREWORK PARTICLE
# ============================================================

class FireworkParticle:

    def __init__(
        self,
        x,
        y,
        color,
    ):
        angle = random.uniform(
            0,
            math.tau,
        )

        speed = random.uniform(
            80,
            230,
        )

        self.x = float(x)
        self.y = float(y)

        self.vx = (
            math.cos(angle)
            * speed
        )

        self.vy = (
            math.sin(angle)
            * speed
        )

        self.color = color

        self.life = random.uniform(
            0.8,
            1.5,
        )

        self.max_life = self.life

    def update(self, dt):

        self.x += (
            self.vx * dt
        )

        self.y += (
            self.vy * dt
        )

        self.vx *= (
            1.0
            - min(
                0.7,
                1.3 * dt,
            )
        )

        self.vy *= (
            1.0
            - min(
                0.7,
                1.3 * dt,
            )
        )

        self.vy += (
            70 * dt
        )

        self.life -= dt

    def draw(self, surface):

        if self.life <= 0:
            return

        alpha = int(
            255
            * clamp(
                self.life
                / self.max_life
            )
        )

        radius = max(
            1,
            int(
                2
                * clamp(
                    self.life
                    / self.max_life
                )
                + 1
            ),
        )

        pygame.draw.circle(
            surface,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha,
            ),
            (
                int(self.x),
                int(self.y),
            ),
            radius,
        )

    @property
    def alive(self):
        return self.life > 0


# ============================================================
# FIREWORK SYSTEM
# ============================================================

class FireworkSystem:

    COLORS = [
        (255, 150, 205),
        (255, 220, 130),
        (180, 150, 255),
        (150, 230, 255),
        (255, 255, 255),
    ]

    def __init__(self):
        self.particles = []

    def burst(
        self,
        x,
        y,
        color=None,
        count=45,
    ):
        if color is None:
            color = random.choice(
                self.COLORS
            )

        for _ in range(count):

            self.particles.append(
                FireworkParticle(
                    x,
                    y,
                    color,
                )
            )

    def update(self, dt):

        for particle in self.particles:
            particle.update(dt)

        self.particles = [
            particle
            for particle in self.particles
            if particle.alive
        ]

    def draw(self, surface):

        for particle in self.particles:
            particle.draw(surface)

    def clear(self):
        self.particles.clear()


# ============================================================
# EFFECTS MANAGER
# ============================================================

class EffectsManager:

    def __init__(
        self,
        width=1280,
        height=720,
    ):
        self.width = width
        self.height = height

        self.flash = ScreenFlash(
            width,
            height,
        )

        self.shake = ScreenShake()

        self.hearts = HeartSystem()

        self.confetti = ConfettiSystem()

        self.fireworks = FireworkSystem()

        self.aura = MagicAura(
            width,
            height,
        )

        self.flame = None

    # ========================================================
    # TRIGGERS
    # ========================================================

    def birthday_burst(
        self,
        x=None,
        y=None,
    ):
        if x is None:
            x = self.width // 2

        if y is None:
            y = self.height // 2

        self.flash.trigger(
            (255, 220, 150),
            strength=150,
            duration=0.35,
        )

        self.shake.trigger(
            strength=5,
            duration=0.25,
        )

        self.hearts.burst(
            x,
            y,
            count=18,
        )

        self.confetti.burst(
            x,
            y,
            count=100,
        )

        self.fireworks.burst(
            x,
            y,
            count=50,
        )

    def celebration_burst(
        self,
        x=None,
        y=None,
    ):
        if x is None:
            x = self.width // 2

        if y is None:
            y = self.height // 2

        self.flash.trigger(
            (255, 180, 220),
            strength=110,
            duration=0.25,
        )

        self.confetti.burst(
            x,
            y,
            count=90,
        )

        self.hearts.burst(
            x,
            y,
            count=15,
        )

    def finale_burst(
        self,
        x=None,
        y=None,
    ):
        if x is None:
            x = self.width // 2

        if y is None:
            y = 210

        self.flash.trigger(
            (255, 220, 150),
            strength=180,
            duration=0.45,
        )

        self.shake.trigger(
            strength=7,
            duration=0.35,
        )

        self.confetti.burst(
            self.width // 2,
            0,
            count=130,
        )

        self.fireworks.burst(
            x,
            y,
            count=70,
        )

        self.hearts.burst(
            self.width // 2,
            self.height // 2,
            count=24,
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        self.flash.update(dt)
        self.shake.update(dt)

        self.hearts.update(dt)
        self.confetti.update(dt)
        self.fireworks.update(dt)

        self.aura.update(dt)

        if self.flame is not None:
            self.flame.update(dt)

    # ========================================================
    # DRAW
    # ========================================================

    def draw_overlay(
        self,
        surface,
    ):
        self.hearts.draw(surface)
        self.confetti.draw(surface)
        self.fireworks.draw(surface)

        self.flash.draw(surface)

    # ========================================================
    # CAMERA
    # ========================================================

    def camera_offset(self):
        return self.shake.offset()

    # ========================================================
    # FLAME
    # ========================================================

    def set_flame(
        self,
        x,
        y,
    ):
        self.flame = CandleFlame(
            x,
            y,
        )

    def clear_flame(self):
        self.flame = None

    def draw_flame(
        self,
        surface,
    ):
        if self.flame is not None:
            self.flame.draw(
                surface
            )

    # ========================================================
    # RESET
    # ========================================================

    def clear(self):

        self.hearts.clear()
        self.confetti.clear()
        self.fireworks.clear()

        self.flash.alpha = 0.0

        self.shake.timer = 0.0
        self.shake.strength = 0.0

        self.flame = None