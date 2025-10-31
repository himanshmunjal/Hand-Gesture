# gesture_control.py (Enhanced)
import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional


class GestureControl:
    """
    MediaPipe-based gesture detector with:
      - Dynamic sensitivity (based on confidence)
      - Hand confidence bar
      - Center guide box overlay
    """
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Gesture state
        self.previous_position = None
        self.position_history = []
        self.max_history = 6
        self.gesture_threshold = 0.035
        self.current_direction = None
        self.gesture_cooldown = 0
        self.max_cooldown = 4

        # Hand detection tracking
        self.no_hand_frames = 0
        self.max_no_hand_frames = 12
        self.last_confidence = 0.0

    def detect_gestures(self, frame: np.ndarray) -> Tuple[Optional[str], bool, np.ndarray]:
        """
        Input: BGR frame
        Output: (direction, is_pinching, annotated_frame)
        """
        annotated = frame.copy()
        direction = None
        is_pinching = False
        dynamic_thresh = self.gesture_threshold

        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            # Default confidence
            confidence = 0.0

            if results and results.multi_hand_landmarks and results.multi_handedness:
                hand_data = results.multi_handedness[0]
                confidence = hand_data.classification[0].score
                self.last_confidence = confidence
            else:
                self.last_confidence = 0.0

            # Dynamic sensitivity: lower threshold = more sensitive
            if self.last_confidence > 0.8:
                dynamic_thresh = 0.02
            elif self.last_confidence > 0.5:
                dynamic_thresh = 0.03
            else:
                dynamic_thresh = 0.05

            if results and results.multi_hand_landmarks:
                self.no_hand_frames = 0
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                        self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )

                    wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                    current_pos = np.array([wrist.x, wrist.y], dtype=float)

                    # smoothing
                    self.position_history.append(current_pos)
                    if len(self.position_history) > self.max_history:
                        self.position_history.pop(0)
                    smoothed = np.mean(self.position_history, axis=0)

                    if self.previous_position is not None and self.gesture_cooldown <= 0:
                        movement = smoothed - self.previous_position
                        dist = np.linalg.norm(movement)
                        if dist > dynamic_thresh:
                            if abs(movement[0]) > abs(movement[1]):
                                direction = "RIGHT" if movement[0] > 0 else "LEFT"
                            else:
                                direction = "DOWN" if movement[1] > 0 else "UP"

                            if direction != self.current_direction:
                                self.current_direction = direction
                                self.gesture_cooldown = self.max_cooldown

                    # Pinch detection
                    thumb = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                    index = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    distance = np.linalg.norm(np.array([thumb.x, thumb.y]) - np.array([index.x, index.y]))
                    is_pinching = distance < 0.05

                    if is_pinching:
                        cv2.putText(annotated, "SPEED BOOST!", (10, 35),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        cv2.circle(annotated,
                                   (int(thumb.x * frame.shape[1]), int(thumb.y * frame.shape[0])),
                                   8, (0, 255, 255), -1)

                    self.previous_position = smoothed

            else:
                self.no_hand_frames += 1
                if self.no_hand_frames > self.max_no_hand_frames:
                    self.reset_gesture_state()

            if self.gesture_cooldown > 0:
                self.gesture_cooldown -= 1

            # Direction display
            if self.current_direction:
                cv2.putText(annotated, f"Direction: {self.current_direction}",
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            # Confidence meter (bottom-left)
            self._draw_confidence_bar(annotated, self.last_confidence)

            # Center guide box
            self._draw_center_box(annotated)

            status = "Hand Detected" if (results and results.multi_hand_landmarks) else "No Hand"
            cv2.putText(annotated, status, (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        except Exception as e:
            # avoid crash
            cv2.putText(annotated, f"Gesture Error", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        return self.current_direction, is_pinching, annotated

    # --- Helper Draw Functions ---
    def _draw_confidence_bar(self, frame, confidence: float):
        """Draws confidence bar in bottom-left corner"""
        h, w, _ = frame.shape
        bar_w, bar_h = 200, 20
        x, y = 20, h - 50
        cv2.rectangle(frame, (x, y), (x + bar_w, y + bar_h), (80, 80, 80), -1)
        filled = int(bar_w * confidence)
        color = (0, int(255 * confidence), 255 - int(255 * confidence))
        cv2.rectangle(frame, (x, y), (x + filled, y + bar_h), color, -1)
        cv2.putText(frame, f"Confidence: {int(confidence * 100)}%", (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def _draw_center_box(self, frame):
        """Draws translucent center guide box"""
        h, w, _ = frame.shape
        box_w, box_h = int(w * 0.4), int(h * 0.5)
        x1, y1 = (w - box_w) // 2, (h - box_h) // 2
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x1 + box_w, y1 + box_h), (0, 255, 0), 2)
        alpha = 0.25
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    def reset_gesture_state(self):
        self.previous_position = None
        self.position_history = []
        self.current_direction = None
        self.gesture_cooldown = 0
        self.no_hand_frames = 0

    def cleanup(self):
        try:
            self.hands.close()
        except Exception:
            pass
