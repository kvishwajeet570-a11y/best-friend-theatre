import pygame
import math


class Slide:

    def __init__(
        self,
        title="",
        subtitle="",
        duration=4.0,
        background=(8, 8, 25),
        draw_callback=None
    ):
        self.title = title
        self.subtitle = subtitle
        self.duration = duration
        self.background = background
        self.draw_callback = draw_callback


class SlideShow:

    def __init__(
        self,
        surface,
        width,
        height,
        slides=None
    ):

        self.surface = surface

        self.width = width
        self.height = height

        self.slides = slides or []

        self.index = 0

        self.time = 0.0

        self.transition_time = 0.0
        self.transition_duration = 0.85

        self.transitioning = False

        self.transition_type = "fade"

        self.direction = 1

        self.auto_play = True

        self.paused = False

        self.finished = False

        # ----------------------------------------------------
        # Fonts
        # ----------------------------------------------------

        self.font_title = pygame.font.SysFont(
            "segoeuisemibold",
            64
        )

        self.font_subtitle = pygame.font.SysFont(
            "segoeui",
            26
        )

        self.font_counter = pygame.font.SysFont(
            "segoeui",
            17
        )

    # ========================================================
    # ADD SLIDE
    # ========================================================

    def add_slide(
        self,
        title="",
        subtitle="",
        duration=4.0,
        background=(8, 8, 25),
        draw_callback=None
    ):

        self.slides.append(
            Slide(
                title=title,
                subtitle=subtitle,
                duration=duration,
                background=background,
                draw_callback=draw_callback
            )
        )

    # ========================================================
    # CURRENT SLIDE
    # ========================================================

    @property
    def current_slide(self):

        if not self.slides:
            return None

        return self.slides[
            max(
                0,
                min(
                    self.index,
                    len(self.slides) - 1
                )
            )
        ]

    # ========================================================
    # EASING
    # ========================================================

    @staticmethod
    def ease_out_cubic(t):

        t = max(
            0.0,
            min(
                1.0,
                t
            )
        )

        return 1 - (1 - t) ** 3

    @staticmethod
    def ease_in_out(t):

        t = max(
            0.0,
            min(
                1.0,
                t
            )
        )

        if t < 0.5:

            return 4 * t * t * t

        return 1 - (
            (-2 * t + 2) ** 3
        ) / 2

    # ========================================================
    # START
    # ========================================================

    def start(self):

        self.index = 0

        self.time = 0.0

        self.transition_time = 0.0

        self.transitioning = False

        self.finished = False

        self.paused = False

    # ========================================================
    # NEXT
    # ========================================================

    def next(
        self,
        transition="slide"
    ):

        if not self.slides:
            return

        if self.index >= len(
            self.slides
        ) - 1:

            self.finished = True

            return

        self.direction = 1

        self.begin_transition(
            transition
        )

    # ========================================================
    # PREVIOUS
    # ========================================================

    def previous(
        self,
        transition="slide"
    ):

        if not self.slides:
            return

        if self.index <= 0:
            return

        self.direction = -1

        self.begin_transition(
            transition
        )

    # ========================================================
    # GO TO
    # ========================================================

    def goto(
        self,
        index,
        transition="fade"
    ):

        if not self.slides:
            return

        index = max(
            0,
            min(
                index,
                len(self.slides) - 1
            )
        )

        if index == self.index:
            return

        self.direction = (
            1
            if index > self.index
            else -1
        )

        self.target_index = index

        self.begin_transition(
            transition
        )

    # ========================================================
    # TRANSITION
    # ========================================================

    def begin_transition(
        self,
        transition="slide"
    ):

        if self.transitioning:
            return

        self.transition_type = transition

        self.transition_time = 0.0

        self.transitioning = True

        self.target_index = (
            self.index
            + self.direction
        )

        self.target_index = max(
            0,
            min(
                self.target_index,
                len(self.slides) - 1
            )
        )

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, dt):

        if not self.slides:
            return

        if self.paused:
            return

        # ----------------------------------------------------
        # Transition
        # ----------------------------------------------------

        if self.transitioning:

            self.transition_time += dt

            if (
                self.transition_time
                >= self.transition_duration
            ):

                self.index = self.target_index

                self.time = 0.0

                self.transitioning = False

                self.transition_time = 0.0

            return

        # ----------------------------------------------------
        # Current slide timer
        # ----------------------------------------------------

        self.time += dt

        if (
            self.auto_play
            and self.current_slide
            and self.time
            >= self.current_slide.duration
        ):

            self.next(
                transition="slide"
            )

    # ========================================================
    # DRAW BACKGROUND
    # ========================================================

    def draw_background(
        self,
        surface,
        slide
    ):

        surface.fill(
            slide.background
        )

    # ========================================================
    # DRAW DEFAULT TEXT
    # ========================================================

    def draw_default_content(
        self,
        surface,
        slide,
        alpha=255,
        offset_x=0,
        scale=1.0
    ):

        if slide.title:

            title = self.font_title.render(
                slide.title,
                True,
                (
                    255,
                    235,
                    250
                )
            )

            title = pygame.transform.rotozoom(
                title,
                0,
                scale
            )

            title.set_alpha(
                int(alpha)
            )

            surface.blit(
                title,
                title.get_rect(
                    center=(
                        self.width // 2
                        + offset_x,
                        self.height // 2 - 35
                    )
                )
            )

        if slide.subtitle:

            subtitle = self.font_subtitle.render(
                slide.subtitle,
                True,
                (
                    225,
                    215,
                    240
                )
            )

            subtitle.set_alpha(
                int(alpha)
            )

            surface.blit(
                subtitle,
                subtitle.get_rect(
                    center=(
                        self.width // 2
                        + offset_x,
                        self.height // 2 + 55
                    )
                )
            )

    # ========================================================
    # DRAW PROGRESS
    # ========================================================

    def draw_progress(
        self,
        surface
    ):

        if not self.slides:
            return

        total = len(
            self.slides
        )

        gap = 8

        width = 280

        x = (
            self.width
            - width
        ) // 2

        y = self.height - 32

        # background

        pygame.draw.rect(
            surface,
            (
                55,
                45,
                70
            ),
            (
                x,
                y,
                width,
                3
            ),
            border_radius=2
        )

        progress = (
            self.index + 1
        ) / total

        pygame.draw.rect(
            surface,
            (
                255,
                150,
                215
            ),
            (
                x,
                y,
                int(
                    width
                    * progress
                ),
                3
            ),
            border_radius=2
        )

        # slide number

        counter = self.font_counter.render(
            f"{self.index + 1:02d} / {total:02d}",
            True,
            (
                165,
                150,
                185
            )
        )

        surface.blit(
            counter,
            counter.get_rect(
                center=(
                    self.width // 2,
                    y - 15
                )
            )
        )

    # ========================================================
    # DRAW TRANSITION
    # ========================================================

    def draw_transition(
        self,
        surface
    ):

        if not self.transitioning:
            return

        progress = (
            self.transition_time
            / self.transition_duration
        )

        progress = max(
            0.0,
            min(
                1.0,
                progress
            )
        )

        eased = self.ease_in_out(
            progress
        )

        old_slide = self.slides[
            self.index
        ]

        new_slide = self.slides[
            self.target_index
        ]

        # ----------------------------------------------------
        # Render old/new slides
        # ----------------------------------------------------

        old_surface = pygame.Surface(
            (
                self.width,
                self.height
            )
        )

        new_surface = pygame.Surface(
            (
                self.width,
                self.height
            )
        )

        self.draw_background(
            old_surface,
            old_slide
        )

        self.draw_background(
            new_surface,
            new_slide
        )

        # ----------------------------------------------------
        # Fade
        # ----------------------------------------------------

        if self.transition_type == "fade":

            old_surface.set_alpha(
                int(
                    255
                    * (1 - eased)
                )
            )

            new_surface.set_alpha(
                int(
                    255
                    * eased
                )
            )

            surface.blit(
                old_surface,
                (0, 0)
            )

            surface.blit(
                new_surface,
                (0, 0)
            )

        # ----------------------------------------------------
        # Zoom
        # ----------------------------------------------------

        elif self.transition_type == "zoom":

            old_scale = 1.0 + (
                eased * 0.08
            )

            new_scale = 0.92 + (
                eased * 0.08
            )

            old_surface = pygame.transform.smoothscale(
                old_surface,
                (
                    int(
                        self.width
                        * old_scale
                    ),
                    int(
                        self.height
                        * old_scale
                    )
                )
            )

            new_surface = pygame.transform.smoothscale(
                new_surface,
                (
                    int(
                        self.width
                        * new_scale
                    ),
                    int(
                        self.height
                        * new_scale
                    )
                )
            )

            old_surface.set_alpha(
                int(
                    255
                    * (1 - eased)
                )
            )

            new_surface.set_alpha(
                int(
                    255
                    * eased
                )
            )

            surface.blit(
                old_surface,
                old_surface.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2
                    )
                )
            )

            surface.blit(
                new_surface,
                new_surface.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2
                    )
                )
            )

        # ----------------------------------------------------
        # Horizontal slide
        # ----------------------------------------------------

        else:

            distance = (
                self.width
            )

            old_x = int(
                -distance
                * eased
                * self.direction
            )

            new_x = int(
                distance
                * (1 - eased)
                * self.direction
            )

            surface.blit(
                old_surface,
                (
                    old_x,
                    0
                )
            )

            surface.blit(
                new_surface,
                (
                    new_x,
                    0
                )
            )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        if not self.slides:
            return

        slide = self.current_slide

        # ----------------------------------------------------
        # Normal rendering
        # ----------------------------------------------------

        if not self.transitioning:

            self.draw_background(
                self.surface,
                slide
            )

            # custom drawing

            if slide.draw_callback:

                slide.draw_callback(
                    self.surface,
                    self
                )

            else:

                self.draw_default_content(
                    self.surface,
                    slide
                )

        # ----------------------------------------------------
        # Transition rendering
        # ----------------------------------------------------

        else:

            self.draw_transition(
                self.surface
            )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        self.draw_progress(
            self.surface
        )

    # ========================================================
    # PAUSE
    # ========================================================

    def toggle_pause(self):

        self.paused = not self.paused

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        self.start()

    # ========================================================
    # EVENT HANDLER
    # ========================================================

    def handle_event(
        self,
        event
    ):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RIGHT:

                self.next(
                    "slide"
                )

            elif event.key == pygame.K_LEFT:

                self.previous(
                    "slide"
                )

            elif event.key == pygame.K_SPACE:

                self.next(
                    "fade"
                )

            elif event.key == pygame.K_p:

                self.toggle_pause()

            elif event.key == pygame.K_HOME:

                self.goto(
                    0,
                    "zoom"
                )

            elif event.key == pygame.K_END:

                self.goto(
                    len(self.slides) - 1,
                    "zoom"
                )

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                self.next(
                    "slide"
                )

            elif event.button == 3:

                self.previous(
                    "slide"
                )

    # ========================================================
    # COMPLETE
    # ========================================================

    @property
    def is_finished(self):

        return self.finished