import os
import pygame


class AudioManager:
    """
    Central audio manager for Best Friend Theatre.

    Music:
        assets/music/birthday.mp3

    Optional music:
        intro.mp3
        garden.mp3
        cake.mp3
        finale.mp3

    Optional sound effects:
        click.wav
        magic.wav
        pop.wav
        firework.wav
        candle.wav
        celebration.wav
        wing.wav
    """

    def __init__(
        self,
        music_dir="assets/music",
        sound_dir="assets/sounds",
    ):
        self.music_dir = music_dir
        self.sound_dir = sound_dir

        self.music_volume = 0.65
        self.sound_volume = 0.80

        self.current_music = None
        self.sounds = {}

        self.initialized = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512,
                )

            self.initialized = True

        except pygame.error as exc:
            print(
                f"[AudioManager] Mixer unavailable: {exc}"
            )
            return

        self._load_sounds()

    # =========================================================
    # PATH HELPERS
    # =========================================================

    def _music_path(self, filename):
        return os.path.join(
            self.music_dir,
            filename,
        )

    def _sound_path(self, filename):
        return os.path.join(
            self.sound_dir,
            filename,
        )

    # =========================================================
    # SOUND EFFECTS
    # =========================================================

    def _load_sounds(self):

        sound_files = {
            "click": "click.wav",
            "magic": "magic.wav",
            "pop": "pop.wav",
            "firework": "firework.wav",
            "candle": "candle.wav",
            "celebration": "celebration.wav",
            "wing": "wing.wav",
        }

        for name, filename in sound_files.items():

            path = self._sound_path(
                filename
            )

            if (
                not os.path.isfile(path)
                or os.path.getsize(path) == 0
            ):
                print(
                    f"[AudioManager] Missing sound: {filename}"
                )
                continue

            try:

                sound = pygame.mixer.Sound(
                    path
                )

                sound.set_volume(
                    self.sound_volume
                )

                self.sounds[name] = sound

                print(
                    f"[AudioManager] Loaded sound: {filename}"
                )

            except pygame.error as exc:

                print(
                    f"[AudioManager] Could not load "
                    f"{filename}: {exc}"
                )

    def play_sound(self, name):

        if not self.initialized:
            return False

        sound = self.sounds.get(name)

        if sound is None:
            return False

        try:

            sound.play()

            return True

        except pygame.error:

            return False

    # =========================================================
    # MUSIC
    # =========================================================

    def play_music(
        self,
        filename,
        loops=0,
        fade_ms=1200,
        start=0.0,
    ):
        """
        Play music from assets/music.

        loops=0 means:
            play once

        loops=-1 means:
            infinite loop
        """

        if not self.initialized:
            return False

        path = self._music_path(
            filename
        )

        if (
            not os.path.isfile(path)
            or os.path.getsize(path) == 0
        ):
            print(
                f"[AudioManager] Music not found: {filename}"
            )
            return False

        try:

            pygame.mixer.music.load(
                path
            )

            pygame.mixer.music.set_volume(
                self.music_volume
            )

            pygame.mixer.music.play(
                loops=loops,
                fade_ms=fade_ms,
                start=max(
                    0.0,
                    float(start),
                ),
            )

            self.current_music = filename

            print(
                f"[AudioManager] Playing music: {filename}"
            )

            return True

        except pygame.error as exc:

            print(
                f"[AudioManager] Could not play "
                f"{filename}: {exc}"
            )

            return False

    def stop_music(
        self,
        fade_ms=1000,
    ):

        if not self.initialized:
            return

        try:

            pygame.mixer.music.fadeout(
                fade_ms
            )

            self.current_music = None

        except pygame.error:
            pass

    def pause_music(self):

        if not self.initialized:
            return

        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass

    def resume_music(self):

        if not self.initialized:
            return

        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass

    def toggle_music(self):

        if not self.initialized:
            return

        try:

            if pygame.mixer.music.get_busy():
                self.pause_music()
            else:
                self.resume_music()

        except pygame.error:
            pass

    # =========================================================
    # VOLUME
    # =========================================================

    def set_music_volume(
        self,
        volume,
    ):

        self.music_volume = max(
            0.0,
            min(
                1.0,
                float(volume),
            ),
        )

        if self.initialized:

            try:

                pygame.mixer.music.set_volume(
                    self.music_volume
                )

            except pygame.error:
                pass

    def set_sound_volume(
        self,
        volume,
    ):

        self.sound_volume = max(
            0.0,
            min(
                1.0,
                float(volume),
            ),
        )

        for sound in self.sounds.values():

            sound.set_volume(
                self.sound_volume
            )

    # =========================================================
    # BIRTHDAY MUSIC
    # =========================================================

    def start_birthday_music(self):

        """
        Search for the best available birthday track.

        Priority:
            birthday.mp3
            finale.mp3
            intro.mp3
            garden.mp3
            cake.mp3

        Birthday track is played ONCE,
        not infinitely looped.
        """

        preferred_music = [
            "birthday.mp3",
            "finale.mp3",
            "intro.mp3",
            "garden.mp3",
            "cake.mp3",
        ]

        for filename in preferred_music:

            path = self._music_path(
                filename
            )

            if (
                os.path.isfile(path)
                and os.path.getsize(path) > 0
            ):

                return self.play_music(
                    filename,
                    loops=0,
                    fade_ms=1200,
                )

        print(
            "[AudioManager] No birthday music available."
        )

        print(
            "[AudioManager] Add:"
            " assets/music/birthday.mp3"
        )

        return False

    # =========================================================
    # MUSIC STATE
    # =========================================================

    def music_is_playing(self):

        if not self.initialized:
            return False

        try:

            return pygame.mixer.music.get_busy()

        except pygame.error:

            return False

    def music_position(self):

        """
        Return approximate current music position
        in seconds.

        Pygame reports milliseconds.
        """

        if not self.initialized:
            return 0.0

        try:

            position = (
                pygame.mixer.music.get_pos()
            )

            if position < 0:
                return 0.0

            return position / 1000.0

        except pygame.error:

            return 0.0

    # =========================================================
    # CLEANUP
    # =========================================================

    def shutdown(self):

        if not self.initialized:
            return

        try:

            pygame.mixer.music.stop()
            pygame.mixer.quit()

        except pygame.error:
            pass