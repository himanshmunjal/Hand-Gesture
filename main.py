# main.py
import cv2
import pygame
import threading
import time
import numpy as np
from gesture_control import GestureControl
from snake_game import SnakeGame


class DualViewSnakeGame:
    """
    Main application:
      - Fullscreen window sized to display resolution
      - Left half: Snake game surface
      - Right half: Camera feed (annotated) surface
      - Background thread reads camera frames and runs gesture detection
    """
    def __init__(self):
        pygame.init()
        pygame.font.init()

        # Determine display resolution and use full coverage
        info = pygame.display.Info()
        self.screen_width = max(800, info.current_w)  # fallback to at least 800
        self.screen_height = max(600, info.current_h)  # fallback to at least 600

        # Create a resizable window that initially fills the screen
        # Use fullscreen? Here we set a window that matches display size for compatibility
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("🐍 Gesture-Controlled Snake (Full Coverage)")

        # Split geometry: left = game, right = camera
        self.left_width = self.screen_width // 2
        self.right_width = self.screen_width - self.left_width
        self.height = self.screen_height

        # Game is sized to left pane
        self.game = SnakeGame(width=self.left_width, height=self.height)

        # Gesture controller
        self.gesture_controller = GestureControl()

        # Camera capture
        self.cap = None
        self.camera_ready = False

        # Threading & shared state
        self.running = True
        self.gesture_thread = None
        self.frame_lock = threading.Lock()
        self.current_gesture = None
        self.is_pinching = False
        self.annotated_frame = None

        # Timing
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.last_game_update = time.time()

    def initialize_camera(self) -> bool:
        """Try camera indices and initialize capture; returns True if successful."""
        for idx in range(3):
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_ANY)
                if cap is None or not cap.isOpened():
                    try:
                        cap.release()
                    except Exception:
                        pass
                    continue
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                cap.set(cv2.CAP_PROP_FPS, 30)
                ret, frame = cap.read()
                if ret and frame is not None:
                    self.cap = cap
                    self.camera_ready = True
                    print(f"Camera initialized at index {idx}")
                    return True
                else:
                    try:
                        cap.release()
                    except Exception:
                        pass
            except Exception as e:
                print("Camera init error idx", idx, e)
        print("Unable to open camera; continuing with placeholder.")
        return False

    def gesture_detection_loop(self):
        """Background thread: read camera frames and update gesture state."""
        print("Gesture detection thread started")
        processed = 0
        while self.running:
            if not self.cap:
                time.sleep(0.05)
                continue
            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue
            frame = cv2.flip(frame, 1)  # mirror

            try:
                gesture, pinching, annotated = self.gesture_controller.detect_gestures(frame)
                with self.frame_lock:
                    self.current_gesture = gesture
                    self.is_pinching = pinching
                    self.annotated_frame = annotated.copy()
                processed += 1
            except Exception:
                # Keep thread alive on transient errors
                time.sleep(0.02)
        print(f"Gesture thread stopped. Frames processed: {processed}")

    def draw_split_view(self, camera_frame):
        """Draw left (game) and right (camera) into window."""
        # Clear main screen
        self.screen.fill((0, 0, 0))

        # Recompute split sizes in case window was resized
        self.left_width = self.screen.get_width() // 2
        self.right_width = self.screen.get_width() - self.left_width
        self.height = self.screen.get_height()

        # Draw game to left surface
        game_surface = pygame.Surface((self.left_width, self.height))
        self.game.width = self.left_width
        self.game.height = self.height
        self.game.grid_width = max(4, self.left_width // self.game.grid_size)
        self.game.grid_height = max(4, self.height // self.game.grid_size)
        self.game.screen = game_surface
        self.game.draw()
        self.screen.blit(game_surface, (0, 0))

        # Divider
        pygame.draw.line(self.screen, (100, 100, 100), (self.left_width, 0), (self.left_width, self.height), 3)

        # Camera pane
        if camera_frame is not None:
            try:
                # Convert BGR -> RGB and resize to right pane
                rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
                rgb = cv2.resize(rgb, (self.right_width, self.height), interpolation=cv2.INTER_LINEAR)
                frame_surface = pygame.image.frombuffer(rgb.tobytes(), (self.right_width, self.height), 'RGB')
                self.screen.blit(frame_surface, (self.left_width, 0))
            except Exception:
                self.draw_camera_placeholder("Error rendering camera")
        else:
            self.draw_camera_placeholder("Camera not available")

        # Instructions overlay on right
        font = pygame.font.Font(None, 20)
        lines = [
            "CONTROLS:",
            "Move hand to change direction",
            "Pinch (thumb+index) = Speed boost",
            "SPACE = Pause",
            "SHOW 'UP' when GAME OVER to restart",
            "ESC = Quit"
        ]
        y0 = max(10, self.height - 140)
        for i, line in enumerate(lines):
            txt = font.render(line, True, (220, 220, 220))
            self.screen.blit(txt, (self.left_width + 10, y0 + i * 20))

        # Flip display
        pygame.display.flip()

    def draw_camera_placeholder(self, message: str):
        rect = pygame.Rect(self.left_width, 0, self.right_width, self.height)
        pygame.draw.rect(self.screen, (30, 30, 30), rect)
        font = pygame.font.Font(None, 30)
        text = font.render(message, True, (200, 200, 200))
        text_rect = text.get_rect(center=(self.left_width + self.right_width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

    def cleanup(self):
        """Graceful cleanup of threads, camera, mediapipe, pygame."""
        print("Cleaning up...")
        self.running = False
        if self.gesture_thread and self.gesture_thread.is_alive():
            self.gesture_thread.join(timeout=2.0)
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
        try:
            self.gesture_controller.cleanup()
        except Exception:
            pass
        try:
            if self.game.score > self.game.high_score:
                self.game.high_score = self.game.score
                self.game.save_high_score()
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
        print("Cleanup complete.")

    def run(self):
        """Main loop: handle events, apply gestures, update game, render."""
        _ = self.initialize_camera()  # best-effort; continue without camera if fails

        # start gesture thread
        self.gesture_thread = threading.Thread(target=self.gesture_detection_loop, daemon=True)
        self.gesture_thread.start()

        print("Starting Gesture-Controlled Snake. Press ESC to exit.")
        try:
            while self.running:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        self.running = False
                    elif ev.type == pygame.VIDEORESIZE:
                        # maintain new window size (pygame takes care)
                        self.screen = pygame.display.set_mode((ev.w, ev.h), pygame.RESIZABLE)
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE:
                            self.running = False
                        elif ev.key == pygame.K_SPACE:
                            self.game.toggle_pause()

                # Get latest gesture safely
                with self.frame_lock:
                    gesture = self.current_gesture
                    pinching = self.is_pinching
                    cam_frame = self.annotated_frame.copy() if self.annotated_frame is not None else None

                # Apply gesture (direction)
                if gesture:
                    self.game.change_direction(gesture)
                    if self.game.game_over:
                        # restart when 'UP' shown
                        self.game.handle_restart(gesture)

                # Apply speed boost
                self.game.set_speed_boost(pinching)

                # Update game using its current speed
                now = time.time()
                speed = self.game.get_current_speed()
                if now - self.last_game_update >= 1.0 / speed:
                    self.game.update()
                    self.last_game_update = now

                # Draw everything
                self.draw_split_view(cam_frame)

                # Cap FPS
                self.clock.tick(self.target_fps)

        except KeyboardInterrupt:
            print("Interrupted by user.")
        except Exception as e:
            print("Runtime error in main loop:", e)
        finally:
            self.cleanup()


def main():
    app = DualViewSnakeGame()
    app.run()


if __name__ == "__main__":
    main()
