import pygame
import random
import math


# ============================================================
# PARTICLE
# ============================================================

class Particle:

    def __init__(
        self,
        x,
        y,
        vx=0.0,
        vy=0.0,
        color=(255, 255, 255),
        size=4,
        life=2.0,
        gravity=0.0,
        friction=1.0,
        shape="circle",
        rotation=0.0
    ):

        self.x = float(x)
        self.y = float(y)

        self.vx = float(vx)
        self.vy = float(vy)

        self.color = color

        self.size = float(size)

        self.life = float(life)
        self.max_life = max(
            0.001,
            float(life)
        )

        self.gravity = float(gravity)

        self.friction = float(friction)

        self.shape = shape

        self.rotation = float(rotation)

        self.rotation_speed = random.uniform(
            -5.0,
            5.0
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vy += self.gravity * dt

        self.vx *= self.friction
        self.vy *= self.friction

        self.rotation += (
            self.rotation_speed
            * dt
        )

        self.life -= dt

        return self.life > 0

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, surface):

        if self.life <= 0:
            return

        alpha = int(
            255
            * max(
                0.0,
                min(
                    1.0,
                    self.life
                    / self.max_life
                )
            )
        )

        size = max(
            1,
            int(self.size)
        )

        color = (
            self.color[0],
            self.color[1],
            self.color[2],
            alpha
        )

        # ----------------------------------------------------
        # Circle
        # ----------------------------------------------------

        if self.shape == "circle":

            pygame.draw.circle(
                surface,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                size
            )

        # ----------------------------------------------------
        # Square
        # ----------------------------------------------------

        elif self.shape == "square":

            pygame.draw.rect(
                surface,
                color,
                (
                    int(self.x - size),
                    int(self.y - size),
                    size * 2,
                    size * 2
                )
            )

        # ----------------------------------------------------
        # Star
        # ----------------------------------------------------

        elif self.shape == "star":

            points = []

            for i in range(10):

                angle = (
                    self.rotation
                    + i
                    * math.pi
                    / 5
                )

                radius = (
                    size
                    if i % 2 == 0
                    else size * 0.4
                )

                points.append(
                    (
                        int(
                            self.x
                            + math.cos(angle)
                            * radius
                        ),
                        int(
                            self.y
                            + math.sin(angle)
                            * radius
                        )
                    )
                )

            pygame.draw.polygon(
                surface,
                color,
                points
            )

        # ----------------------------------------------------
        # Petal
        # ----------------------------------------------------

        elif self.shape == "petal":

            petal = pygame.Surface(
                (
                    size * 4,
                    size * 4
                ),
                pygame.SRCALPHA
            )

            pygame.draw.ellipse(
                petal,
                color,
                (
                    size,
                    size // 2,
                    size * 2,
                    size * 3
                )
            )

            rotated = pygame.transform.rotate(
                petal,
                math.degrees(
                    self.rotation
                )
            )

            surface.blit(
                rotated,
                (
                    int(
                        self.x
                        - rotated.get_width() / 2
                    ),
                    int(
                        self.y
                        - rotated.get_height() / 2
                    )
                )
            )


# ============================================================
# PARTICLE SYSTEM
# ============================================================

class ParticleSystem:

    def __init__(self):

        self.particles = []

    # ========================================================
    # GENERIC EMIT
    # ========================================================

    def emit(
        self,
        x,
        y,
        count=1,
        color=None,
        speed=2.0,
        gravity=0.0,
        life=2.0,
        size=4,
        shape="circle",
        friction=1.0,
        vx=None,
        vy=None
    ):

        if color is None:

            color = random.choice(
                [
                    (255, 255, 255),
                    (255, 220, 120),
                    (255, 150, 210),
                    (150, 210, 255),
                    (190, 150, 255),
                ]
            )

        for _ in range(
            max(0, int(count))
        ):

            if vx is None or vy is None:

                angle = random.uniform(
                    0,
                    math.tau
                )

                particle_speed = random.uniform(
                    speed * 0.45,
                    speed
                )

                pvx = (
                    math.cos(angle)
                    * particle_speed
                )

                pvy = (
                    math.sin(angle)
                    * particle_speed
                )

            else:

                pvx = vx
                pvy = vy

            particle = Particle(
                x=x,
                y=y,
                vx=pvx,
                vy=pvy,
                color=color,
                size=random.uniform(
                    size * 0.65,
                    size * 1.25
                ),
                life=random.uniform(
                    life * 0.65,
                    life
                ),
                gravity=gravity,
                friction=friction,
                shape=shape,
                rotation=random.uniform(
                    0,
                    math.tau
                )
            )

            self.particles.append(
                particle
            )

    # ========================================================
    # MAGIC BURST
    # ========================================================

    def magic_burst(
        self,
        x,
        y,
        count=35
    ):

        colors = [
            (255, 120, 210),
            (255, 220, 120),
            (150, 210, 255),
            (200, 140, 255),
            (150, 255, 210),
        ]

        for _ in range(
            count
        ):

            angle = random.uniform(
                0,
                math.tau
            )

            speed = random.uniform(
                1.5,
                5.5
            )

            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.choice(colors),
                    random.randint(2, 5),
                    random.uniform(
                        0.8,
                        2.2
                    ),
                    0.08,
                    0.985,
                    "star",
                    angle
                )
            )

    # ========================================================
    # CONFETTI
    # ========================================================

    def confetti(
        self,
        x,
        y,
        count=100
    ):

        colors = [
            (255, 80, 160),
            (255, 210, 80),
            (80, 190, 255),
            (100, 240, 160),
            (180, 100, 255),
            (255, 140, 80),
        ]

        for _ in range(
            count
        ):

            angle = random.uniform(
                -math.pi,
                0
            )

            speed = random.uniform(
                3,
                9
            )

            self.particles.append(
                Particle(
                    x + random.uniform(
                        -10,
                        10
                    ),
                    y + random.uniform(
                        -5,
                        5
                    ),
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.choice(colors),
                    random.randint(3, 7),
                    random.uniform(
                        2.5,
                        5.0
                    ),
                    random.uniform(
                        0.08,
                        0.18
                    ),
                    0.995,
                    "square",
                    random.random() * math.tau
                )
            )

    # ========================================================
    # PETALS
    # ========================================================

    def petals(
        self,
        x,
        y,
        count=30
    ):

        colors = [
            (255, 150, 190),
            (255, 190, 215),
            (245, 130, 180),
            (255, 220, 235),
        ]

        for _ in range(
            count
        ):

            self.particles.append(
                Particle(
                    x + random.randint(
                        -150,
                        150
                    ),
                    y + random.randint(
                        -80,
                        80
                    ),
                    random.uniform(
                        -0.8,
                        0.8
                    ),
                    random.uniform(
                        0.5,
                        2.0
                    ),
                    random.choice(colors),
                    random.randint(
                        3,
                        6
                    ),
                    random.uniform(
                        3,
                        6
                    ),
                    0.04,
                    0.995,
                    "petal",
                    random.random() * math.tau
                )
            )

    # ========================================================
    # FIREWORKS
    # ========================================================

    def fireworks(
        self,
        x,
        y,
        count=70
    ):

        colors = [
            (255, 100, 180),
            (255, 220, 100),
            (100, 210, 255),
            (180, 120, 255),
            (100, 255, 190),
        ]

        for _ in range(
            count
        ):

            angle = random.uniform(
                0,
                math.tau
            )

            speed = random.uniform(
                2.0,
                6.0
            )

            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.choice(colors),
                    random.randint(2, 4),
                    random.uniform(
                        1.0,
                        2.0
                    ),
                    0.10,
                    0.985,
                    "star",
                    angle
                )
            )

    # ========================================================
    # SPARKLE
    # ========================================================

    def sparkle(
        self,
        x,
        y,
        count=5
    ):

        for _ in range(
            count
        ):

            self.particles.append(
                Particle(
                    x + random.uniform(
                        -10,
                        10
                    ),
                    y + random.uniform(
                        -10,
                        10
                    ),
                    random.uniform(
                        -0.4,
                        0.4
                    ),
                    random.uniform(
                        -1.0,
                        1.0
                    ),
                    (255, 235, 150),
                    random.randint(
                        2,
                        4
                    ),
                    random.uniform(
                        0.5,
                        1.3
                    ),
                    0,
                    0.98,
                    "star",
                    random.random() * math.tau
                )
            )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        alive = []

        for particle in self.particles:

            if particle.update(dt):

                alive.append(
                    particle
                )

        self.particles = alive

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, surface):

        for particle in self.particles:

            particle.draw(
                surface
            )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self):

        self.particles.clear()

    # ========================================================
    # COUNT
    # ========================================================

    def count(self):

        return len(
            self.particles
        )