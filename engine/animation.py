import math


class Animation:

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    @staticmethod
    def clamp(value, minimum=0.0, maximum=1.0):
        return max(
            minimum,
            min(
                maximum,
                value
            )
        )

    @staticmethod
    def lerp(start, end, progress):
        progress = Animation.clamp(progress)
        return start + (end - start) * progress

    @staticmethod
    def lerp_point(start, end, progress):
        progress = Animation.clamp(progress)

        return (
            Animation.lerp(
                start[0],
                end[0],
                progress
            ),
            Animation.lerp(
                start[1],
                end[1],
                progress
            )
        )

    # =========================================================
    # EASING
    # =========================================================

    @staticmethod
    def linear(t):
        return Animation.clamp(t)

    @staticmethod
    def ease_in_quad(t):
        t = Animation.clamp(t)
        return t * t

    @staticmethod
    def ease_out_quad(t):
        t = Animation.clamp(t)
        return 1 - (1 - t) ** 2

    @staticmethod
    def ease_in_out_quad(t):
        t = Animation.clamp(t)

        if t < 0.5:
            return 2 * t * t

        return 1 - ((-2 * t + 2) ** 2) / 2

    @staticmethod
    def ease_in_cubic(t):
        t = Animation.clamp(t)
        return t ** 3

    @staticmethod
    def ease_out_cubic(t):
        t = Animation.clamp(t)
        return 1 - (1 - t) ** 3

    @staticmethod
    def ease_in_out_cubic(t):
        t = Animation.clamp(t)

        if t < 0.5:
            return 4 * t ** 3

        return 1 - ((-2 * t + 2) ** 3) / 2

    @staticmethod
    def ease_out_quart(t):
        t = Animation.clamp(t)
        return 1 - (1 - t) ** 4

    @staticmethod
    def ease_in_out_quart(t):
        t = Animation.clamp(t)

        if t < 0.5:
            return 8 * t ** 4

        return 1 - ((-2 * t + 2) ** 4) / 2

    @staticmethod
    def ease_out_back(t):
        t = Animation.clamp(t)

        c1 = 1.70158
        c3 = c1 + 1

        return (
            1
            + c3 * (t - 1) ** 3
            + c1 * (t - 1) ** 2
        )

    @staticmethod
    def ease_out_elastic(t):
        t = Animation.clamp(t)

        if t == 0:
            return 0

        if t == 1:
            return 1

        c4 = (
            2
            * math.pi
            / 3
        )

        return (
            2 ** (-10 * t)
            * math.sin(
                (t * 10 - 0.75)
                * c4
            )
            + 1
        )

    # =========================================================
    # FLOATING
    # =========================================================

    @staticmethod
    def float_value(
        time,
        base=0.0,
        amplitude=10.0,
        speed=1.0,
        phase=0.0
    ):
        """
        Smooth floating animation.

        time       -> current time
        base       -> center/base value
        amplitude  -> movement distance
        speed      -> movement speed
        phase      -> optional phase offset
        """

        return (
            base
            + math.sin(
                time * speed + phase
            )
            * amplitude
        )

    # =========================================================
    # PULSE
    # =========================================================

    @staticmethod
    def pulse(
        time,
        scale=1.0,
        amount=0.05,
        speed=2.0,
        phase=0.0
    ):
        return (
            scale
            + math.sin(
                time * speed + phase
            )
            * amount
        )

    # =========================================================
    # BREATHING
    # =========================================================

    @staticmethod
    def breathing(
        time,
        minimum=0.96,
        maximum=1.04,
        speed=1.5
    ):
        wave = (
            math.sin(
                time * speed
            )
            + 1
        ) / 2

        return Animation.lerp(
            minimum,
            maximum,
            wave
        )

    # =========================================================
    # BOUNCE
    # =========================================================

    @staticmethod
    def bounce(
        time,
        amplitude=10.0,
        speed=4.0
    ):
        return abs(
            math.sin(
                time * speed
            )
        ) * amplitude

    # =========================================================
    # SWING
    # =========================================================

    @staticmethod
    def swing(
        time,
        angle=10.0,
        speed=2.0,
        phase=0.0
    ):
        return (
            math.sin(
                time * speed + phase
            )
            * angle
        )

    # =========================================================
    # SHAKE
    # =========================================================

    @staticmethod
    def shake(
        time,
        intensity=5.0,
        speed=30.0
    ):
        return (
            math.sin(
                time * speed
            )
            * intensity
        )

    # =========================================================
    # FADE
    # =========================================================

    @staticmethod
    def fade_in(
        elapsed,
        duration=1.0
    ):
        if duration <= 0:
            return 1.0

        return Animation.clamp(
            elapsed / duration
        )

    @staticmethod
    def fade_out(
        elapsed,
        duration=1.0
    ):
        if duration <= 0:
            return 0.0

        return 1.0 - Animation.clamp(
            elapsed / duration
        )

    # =========================================================
    # SCALE
    # =========================================================

    @staticmethod
    def scale_in(
        elapsed,
        duration=1.0,
        start=0.0,
        end=1.0
    ):
        progress = Animation.ease_out_back(
            Animation.clamp(
                elapsed / duration
            )
        )

        return Animation.lerp(
            start,
            end,
            progress
        )

    # =========================================================
    # SLIDE
    # =========================================================

    @staticmethod
    def slide(
        elapsed,
        duration=1.0,
        start=0.0,
        end=1.0,
        easing="ease_out_cubic"
    ):
        progress = Animation.clamp(
            elapsed / duration
        )

        easing_function = getattr(
            Animation,
            easing,
            Animation.ease_out_cubic
        )

        progress = easing_function(
            progress
        )

        return Animation.lerp(
            start,
            end,
            progress
        )

    # =========================================================
    # TYPEWRITER
    # =========================================================

    @staticmethod
    def typewriter(
        text,
        elapsed,
        characters_per_second=30
    ):
        count = int(
            elapsed
            * characters_per_second
        )

        return text[
            :max(
                0,
                min(
                    len(text),
                    count
                )
            )
        ]

    # =========================================================
    # BLINK
    # =========================================================

    @staticmethod
    def blink(
        time,
        interval=3.5,
        duration=0.12
    ):
        cycle = time % interval

        return cycle < duration

    # =========================================================
    # ORBIT
    # =========================================================

    @staticmethod
    def orbit(
        center_x,
        center_y,
        radius,
        time,
        speed=1.0,
        phase=0.0
    ):
        angle = (
            time * speed
            + phase
        )

        return (
            center_x
            + math.cos(angle) * radius,

            center_y
            + math.sin(angle) * radius
        )

    # =========================================================
    # PARABOLA
    # =========================================================

    @staticmethod
    def parabola(
        progress,
        height=100.0
    ):
        progress = Animation.clamp(
            progress
        )

        return (
            4
            * height
            * progress
            * (1 - progress)
        )

    # =========================================================
    # ROTATION
    # =========================================================

    @staticmethod
    def rotation(
        time,
        speed=90.0,
        start_angle=0.0
    ):
        return (
            start_angle
            + time * speed
        ) % 360

    # =========================================================
    # DELAYED PROGRESS
    # =========================================================

    @staticmethod
    def delayed_progress(
        elapsed,
        delay=0.0,
        duration=1.0
    ):
        if elapsed <= delay:
            return 0.0

        if duration <= 0:
            return 1.0

        return Animation.clamp(
            (
                elapsed - delay
            )
            / duration
        )

    # =========================================================
    # STAGGERED
    # =========================================================

    @staticmethod
    def staggered(
        index,
        total,
        elapsed,
        delay=0.1,
        duration=0.6
    ):
        start_delay = index * delay

        progress = Animation.delayed_progress(
            elapsed,
            start_delay,
            duration
        )

        return Animation.ease_out_cubic(
            progress
        )