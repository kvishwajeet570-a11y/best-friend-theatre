# ============================================================
# BEST FRIEND THEATRE — AUDIO ENGINE
# Desktop + Pygbag/Web Compatible
# ============================================================

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import pygame


class AudioManager:
    """
    Central audio manager for Best Friend Theatre.

    Desktop:
        Prefer birthday.mp3.

    Web / Pygbag:
        Prefer birthday.ogg.

    Optional sound effects are loaded when available.
    Missing sounds never crash the application.
    """

    def __init__(
        self,
        music_dir: str = "assets/music",
        sound_dir: str = "assets/sounds",
    ):
        self.music_dir = Path(music_dir)
        self.sound_dir = Path(sound_dir)

        self.music_volume = 0.72
        self.sfx_volume = 0.85

        self.current_music: Optional[str] = None
        self.music_loaded = False
        self._paused = False

        self.sounds: dict[str, pygame.mixer.Sound] = {}

        self._init_mixer()
        self._load_sounds()

    # ========================================================
    # MIXER
    # ========================================================

    def _init_mixer(self) -> None:
        """Initialize the mixer safely."""

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=2048,
                )

            pygame.mixer.music.set_volume(self.music_volume)

        except Exception as exc:
            print(
                f"[AudioManager] Mixer initialization failed: {exc}"
            )

    # ========================================================
    # WEB / PYGBAG DETECTION
    # ========================================================

    @staticmethod
    def is_web() -> bool:
        """Detect Pygbag / Emscripten browser environment."""

        if sys.platform == "emscripten":
            return True

        if os.environ.get("PYGBAG"):
            return True

        if os.environ.get("EMSCRIPTEN"):
            return True

        return False

    # ========================================================
    # MUSIC FILE HELPERS
    # ========================================================

    def _music_candidates(self) -> list[Path]:
        """
        Return preferred music files.

        Web:
            birthday.ogg first

        Desktop:
            birthday.mp3 first
        """

        mp3 = self.music_dir / "birthday.mp3"
        ogg = self.music_dir / "birthday.ogg"

        if self.is_web():
            return [ogg, mp3]

        return [mp3, ogg]

    def _find_birthday_music(self) -> Optional[Path]:
        """Find the first valid birthday music file."""

        for path in self._music_candidates():

            if path.is_file() and path.stat().st_size > 0:
                return path

        # Fallback music names.
        fallback_names = [
            "finale.ogg",
            "finale.mp3",
            "intro.ogg",
            "intro.mp3",
            "garden.ogg",
            "garden.mp3",
            "cake.ogg",
            "cake.mp3",
        ]

        for name in fallback_names:

            path = self.music_dir / name

            if path.is_file() and path.stat().st_size > 0:
                return path

        return None

    # ========================================================
    # OPTIONAL SOUND EFFECTS
    # ========================================================

    def _load_sounds(self) -> None:
        """
        Load optional sound effects.

        Missing files are completely safe.
        """

        sound_names = [
            "click",
            "magic",
            "pop",
            "firework",
            "candle",
            "celebration",
            "wing",
        ]

        for name in sound_names:

            loaded = False

            if self.is_web():
                extensions = [
                    ".ogg",
                    ".wav",
                    ".mp3",
                ]
            else:
                extensions = [
                    ".wav",
                    ".ogg",
                    ".mp3",
                ]

            for extension in extensions:

                path = self.sound_dir / f"{name}{extension}"

                if not path.is_file():
                    continue

                if path.stat().st_size <= 0:
                    continue

                try:

                    sound = pygame.mixer.Sound(str(path))
                    sound.set_volume(self.sfx_volume)

                    self.sounds[name] = sound

                    print(
                        f"[AudioManager] Loaded sound: "
                        f"{path.name}"
                    )

                    loaded = True
                    break

                except Exception as exc:

                    print(
                        f"[AudioManager] Could not load "
                        f"{path.name}: {exc}"
                    )

            if not loaded:

                print(
                    f"[AudioManager] Missing sound: {name}.wav"
                )

    # ========================================================
    # PLAY SOUND EFFECT
    # ========================================================

    def play_sound(
        self,
        name: str,
        volume: Optional[float] = None,
    ) -> bool:
        """Play an optional sound effect."""

        sound = self.sounds.get(name)

        if sound is None:
            return False

        try:

            if volume is not None:

                volume = max(
                    0.0,
                    min(1.0, float(volume)),
                )

                sound.set_volume(volume)

            else:

                sound.set_volume(self.sfx_volume)

            sound.play()

            return True

        except Exception as exc:

            print(
                f"[AudioManager] Sound play failed "
                f"({name}): {exc}"
            )

            return False

    # ========================================================
    # PLAY MUSIC
    # ========================================================

    def play_music(
        self,
        filename: str,
        loops: int = 0,
        fade_ms: int = 1200,
        start: float = 0.0,
    ) -> bool:
        """
        Play a music file.

        loops=0:
            Play exactly once.
        """

        path = self.music_dir / filename

        if not path.is_file():

            print(
                f"[AudioManager] Missing music: {filename}"
            )

            return False

        if path.stat().st_size <= 0:

            print(
                f"[AudioManager] Empty music file: {filename}"
            )

            return False

        try:

            pygame.mixer.music.stop()

            pygame.mixer.music.load(str(path))

            pygame.mixer.music.set_volume(
                self.music_volume
            )

            if start > 0:

                pygame.mixer.music.play(
                    loops=loops,
                    fade_ms=max(0, int(fade_ms)),
                    start=float(start),
                )

            else:

                pygame.mixer.music.play(
                    loops=loops,
                    fade_ms=max(0, int(fade_ms)),
                )

            self.current_music = filename
            self.music_loaded = True
            self._paused = False

            print(
                f"[AudioManager] Playing music: {filename}"
            )

            return True

        except Exception as exc:

            print(
                f"[AudioManager] Failed to play "
                f"music {filename}: {exc}"
            )

            return False

    # ========================================================
    # BIRTHDAY MUSIC
    # ========================================================

    def start_birthday_music(self) -> bool:
        """
        Automatically select birthday music.

        Desktop:
            birthday.mp3

        Web:
            birthday.ogg
        """

        path = self._find_birthday_music()

        if path is None:

            print(
                "[AudioManager] No birthday music found."
            )

            print(
                "[AudioManager] Expected:"
            )

            print(
                "    assets/music/birthday.mp3"
            )

            print(
                "    assets/music/birthday.ogg"
            )

            return False

        return self.play_music(
            path.name,
            loops=0,
            fade_ms=1200,
            start=0.0,
        )

    # ========================================================
    # MUSIC STATE
    # ========================================================

    def music_is_playing(self) -> bool:
        """Return True when music is currently playing."""

        try:

            return (
                pygame.mixer.music.get_busy()
                and not self._paused
            )

        except Exception:

            return False

    def music_position(self) -> float:
        """
        Return current music position in seconds.
        """

        try:

            position_ms = (
                pygame.mixer.music.get_pos()
            )

            if position_ms < 0:
                return 0.0

            return position_ms / 1000.0

        except Exception:

            return 0.0

    # ========================================================
    # PAUSE
    # ========================================================

    def pause_music(self) -> None:
        """Pause music."""

        try:

            pygame.mixer.music.pause()

            self._paused = True

        except Exception as exc:

            print(
                f"[AudioManager] Pause failed: {exc}"
            )

    # ========================================================
    # RESUME
    # ========================================================

    def resume_music(self) -> None:
        """Resume music."""

        try:

            pygame.mixer.music.unpause()

            self._paused = False

        except Exception as exc:

            print(
                f"[AudioManager] Resume failed: {exc}"
            )

    # ========================================================
    # TOGGLE
    # ========================================================

    def toggle_music(self) -> bool:
        """
        Toggle music pause/resume.

        Returns:
            True  -> playing
            False -> paused
        """

        if self._paused:

            self.resume_music()

            return True

        self.pause_music()

        return False

    # ========================================================
    # MUSIC VOLUME
    # ========================================================

    def set_music_volume(
        self,
        volume: float,
    ) -> None:
        """Set music volume 0.0 to 1.0."""

        self.music_volume = max(
            0.0,
            min(1.0, float(volume)),
        )

        try:

            pygame.mixer.music.set_volume(
                self.music_volume
            )

        except Exception:
            pass

    # ========================================================
    # SFX VOLUME
    # ========================================================

    def set_sfx_volume(
        self,
        volume: float,
    ) -> None:
        """Set SFX volume 0.0 to 1.0."""

        self.sfx_volume = max(
            0.0,
            min(1.0, float(volume)),
        )

        for sound in self.sounds.values():

            try:

                sound.set_volume(
                    self.sfx_volume
                )

            except Exception:
                pass

    # ========================================================
    # STOP MUSIC
    # ========================================================

    def stop_music(
        self,
        fade_ms: int = 500,
    ) -> None:
        """Stop music safely."""

        try:

            if fade_ms > 0:

                pygame.mixer.music.fadeout(
                    int(fade_ms)
                )

            else:

                pygame.mixer.music.stop()

            self._paused = False

        except Exception as exc:

            print(
                f"[AudioManager] Stop failed: {exc}"
            )

    # ========================================================
    # RESTART MUSIC
    # ========================================================

    def restart_music(self) -> bool:
        """Restart currently selected music."""

        if self.current_music:

            return self.play_music(
                self.current_music,
                loops=0,
                fade_ms=700,
                start=0.0,
            )

        return self.start_birthday_music()

    # ========================================================
    # SHUTDOWN
    # ========================================================

    def shutdown(self) -> None:
        """Cleanly shut down audio."""

        try:

            pygame.mixer.music.stop()

        except Exception:
            pass

        try:

            pygame.mixer.stop()

        except Exception:
            pass

        self.music_loaded = False
        self.current_music = None
        self._paused = False