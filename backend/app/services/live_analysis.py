"""
Live interview analysis service.
Runs real AI analysis on video frames from the candidate's camera.
Uses existing ai_engine modules: FaceAnalyzer, DeepfakeDetector, EmotionAnalyzer, TrustCalculator.
"""

import time
import threading
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from app.ai_engine.face_analyzer import FaceAnalyzer
from app.ai_engine.deepfake_detector import DeepfakeDetector
from app.ai_engine.emotion_analyzer import EmotionAnalyzer
from app.ai_engine.trust_calculator import TrustCalculator

LOOKING_AWAY_THRESHOLD_SEC = 3.0
LOOKING_DOWN_THRESHOLD_SEC = 3.0
FACE_ABSENT_THRESHOLD_SEC = 3.0
EXCESSIVE_YAW_THRESHOLD = 18.0
EXCESSIVE_PITCH_THRESHOLD = 18.0


@dataclass
class DetectionEvent:
    event_type: str
    severity: str
    message: str
    confidence: float
    timestamp: float


@dataclass
class GazeTracker:
    """Tracks continuous gaze state over time."""
    looking_away_since: float = 0.0
    looking_away_total_sec: float = 0.0
    looking_down_since: float = 0.0
    looking_down_total_sec: float = 0.0
    looking_away_event_fired: bool = False
    looking_down_event_fired: bool = False

    def update(self, gaze_direction: str, pitch: float, now: float):
        if gaze_direction in ("Left", "Right"):
            if self.looking_away_since == 0:
                self.looking_away_since = now
                self.looking_away_event_fired = False
            elapsed = now - self.looking_away_since
            self.looking_away_total_sec = elapsed
        else:
            if self.looking_away_since > 0:
                self.looking_away_total_sec = now - self.looking_away_since
            self.looking_away_since = 0.0
            self.looking_away_event_fired = False

        if pitch > 15:
            if self.looking_down_since == 0:
                self.looking_down_since = now
                self.looking_down_event_fired = False
            self.looking_down_total_sec = now - self.looking_down_since
        else:
            if self.looking_down_since > 0:
                self.looking_down_total_sec = now - self.looking_down_since
            self.looking_down_since = 0.0
            self.looking_down_event_fired = False


@dataclass
class FaceAbsentTracker:
    """Tracks continuous face absence."""
    absent_since: float = 0.0
    was_present: bool = False
    event_fired: bool = False

    def update(self, face_present: bool, now: float):
        if face_present:
            self.was_present = True
            self.absent_since = 0.0
            self.event_fired = False
        else:
            if self.was_present and self.absent_since == 0:
                self.absent_since = now
                self.event_fired = False


@dataclass
class LiveAnalysisState:
    """Persistent state for one interview's live analysis."""
    interview_id: str
    started_at: float = 0.0

    face_analyzer: Optional[FaceAnalyzer] = None
    deepfake_detector: Optional[DeepfakeDetector] = None
    emotion_analyzer: Optional[EmotionAnalyzer] = None
    trust_calculator: Optional[TrustCalculator] = None

    frame_count: int = 0
    last_analysis_time: float = 0.0

    current_face_count: int = 0
    reference_face_embedding: Optional[np.ndarray] = None

    gaze_tracker: GazeTracker = field(default_factory=GazeTracker)
    face_absent_tracker: FaceAbsentTracker = field(default_factory=FaceAbsentTracker)

    emotion_history: list = field(default_factory=list)
    gaze_history: list = field(default_factory=list)
    pose_history: list = field(default_factory=list)
    face_count_history: list = field(default_factory=list)
    gaze_yaw_history: list = field(default_factory=list)

    events: list = field(default_factory=list)
    event_ids: int = 0

    accumulated_scores: dict = field(default_factory=lambda: {
        "eye_contact_frames": 0,
        "total_frames": 0,
        "looking_away_frames": 0,
        "looking_down_frames": 0,
        "face_present_frames": 0,
        "face_absent_frames": 0,
        "multiple_face_frames": 0,
        "normal_head_frames": 0,
        "excessive_movement_frames": 0,
        "occlusion_frames": 0,
        "deepfake_scores": [],
        "emotion_scores": [],
        "sustained_looking_away_events": 0,
        "sustained_looking_down_events": 0,
    })

    client_events: list = field(default_factory=list)
    last_trust_score: float = 85.0
    last_risk_level: str = "low"

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)


class LiveAnalysisService:
    """Manages live analysis sessions for interviews."""

    def __init__(self):
        self.sessions: dict[str, LiveAnalysisState] = {}
        self._face_analyzer = None
        self._deepfake_detector = None
        self._emotion_analyzer = None
        self._trust_calculator = None
        self._lock = threading.Lock()
        self._initialized = False

    def _ensure_initialized(self):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            try:
                self._face_analyzer = FaceAnalyzer()
            except Exception:
                self._face_analyzer = None
            try:
                self._deepfake_detector = DeepfakeDetector()
            except Exception:
                self._deepfake_detector = None
            try:
                self._emotion_analyzer = EmotionAnalyzer()
            except Exception:
                self._emotion_analyzer = None
            try:
                self._trust_calculator = TrustCalculator()
            except Exception:
                self._trust_calculator = None
            self._initialized = True

    def start_session(self, interview_id: str) -> LiveAnalysisState:
        self._ensure_initialized()
        with self._lock:
            state = LiveAnalysisState(
                interview_id=interview_id,
                started_at=time.time(),
                face_analyzer=self._face_analyzer,
                deepfake_detector=self._deepfake_detector,
                emotion_analyzer=self._emotion_analyzer,
                trust_calculator=self._trust_calculator,
            )
            self.sessions[interview_id] = state
            return state

    def get_state(self, interview_id: str) -> Optional[LiveAnalysisState]:
        return self.sessions.get(interview_id)

    def stop_session(self, interview_id: str) -> Optional[LiveAnalysisState]:
        with self._lock:
            return self.sessions.pop(interview_id, None)

    def _add_event(self, state: LiveAnalysisState, event_type: str, severity: str, message: str, confidence: float):
        state.event_ids += 1
        evt = DetectionEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            confidence=round(confidence, 2),
            timestamp=time.time(),
        )
        state.events.append(evt)
        if len(state.events) > 200:
            state.events = state.events[-200:]

    def _estimate_gaze_direction(self, landmarks: dict) -> str:
        """Estimate gaze direction from iris landmarks (more accurate)."""
        left_iris = landmarks.get("left_iris")
        right_iris = landmarks.get("right_iris")
        left_eye = landmarks.get("left_eye", {})
        right_eye = landmarks.get("right_eye", {})

        if left_iris and right_iris:
            iris_center_x = (left_iris.get("x", 0.5) + right_iris.get("x", 0.5)) / 2
            eye_center_x = (left_eye.get("x", 0.5) + right_eye.get("x", 0.5)) / 2
            offset = iris_center_x - eye_center_x

            if offset > 0.015:
                return "Right"
            elif offset < -0.015:
                return "Left"
            return "Center"

        nose = landmarks.get("nose_tip", {})
        if left_eye and right_eye and nose:
            eye_center_x = (left_eye.get("x", 0.5) + right_eye.get("x", 0.5)) / 2
            nose_x = nose.get("x", 0.5)
            offset = nose_x - eye_center_x
            if offset > 0.03:
                return "Right"
            elif offset < -0.03:
                return "Left"
            return "Center"

        return "Unknown"

    def _classify_head_pose(self, pose_angles: dict) -> str:
        yaw = abs(pose_angles.get("yaw", 0))
        pitch = abs(pose_angles.get("pitch", 0))

        if yaw > EXCESSIVE_YAW_THRESHOLD or pitch > EXCESSIVE_PITCH_THRESHOLD:
            return "Turned Away"
        elif yaw > 12 or pitch > 12:
            return "Angled"
        return "Straight"

    def _compute_eye_contact_score(self, state: LiveAnalysisState) -> float:
        if state.accumulated_scores["total_frames"] == 0:
            return 0
        return round(
            state.accumulated_scores["eye_contact_frames"]
            / state.accumulated_scores["total_frames"]
            * 100,
            1,
        )

    def _compute_body_language_score(self, state: LiveAnalysisState) -> float:
        acc = state.accumulated_scores
        total = acc["total_frames"]
        if total == 0:
            return 50.0

        good = acc["face_present_frames"] + acc["normal_head_frames"]
        bad = acc["face_absent_frames"] + acc["looking_down_frames"] + acc["excessive_movement_frames"]

        score = max(0, min(100, 50 + (good - bad) / total * 50))
        return round(score, 1)

    def _compute_trust_score(self, state: LiveAnalysisState) -> float:
        acc = state.accumulated_scores
        total = acc["total_frames"]
        if total == 0:
            return 85.0

        eye_contact = self._compute_eye_contact_score(state)
        body_lang = self._compute_body_language_score(state)

        deepfake_avg = np.mean(acc["deepfake_scores"]) * 100 if acc["deepfake_scores"] else 85.0
        emotion_avg = np.mean(acc["emotion_scores"]) * 100 if acc["emotion_scores"] else 70.0

        penalty = 0
        penalty += acc["multiple_face_frames"] / total * 30
        penalty += acc["looking_away_frames"] / total * 20
        penalty += acc["looking_down_frames"] / total * 15
        penalty += acc["face_absent_frames"] / total * 25
        penalty += acc["excessive_movement_frames"] / total * 10
        penalty += acc["sustained_looking_away_events"] * 8
        penalty += acc["sustained_looking_down_events"] * 5

        trust = (
            eye_contact * 0.25
            + body_lang * 0.15
            + deepfake_avg * 0.30
            + emotion_avg * 0.15
            + (100 - penalty) * 0.15
        )

        client_events = state.client_events
        tab_switches = sum(1 for e in client_events if e.get("type") == "tab_switch")
        focus_losses = sum(1 for e in client_events if e.get("type") == "focus_loss")
        fullscreen_exits = sum(1 for e in client_events if e.get("type") == "fullscreen_exit")

        trust -= tab_switches * 5
        trust -= focus_losses * 3
        trust -= fullscreen_exits * 4

        return round(max(0, min(100, trust)), 1)

    def _determine_risk_level(self, score: float) -> str:
        if score >= 80:
            return "low"
        elif score >= 60:
            return "medium"
        elif score >= 40:
            return "high"
        return "critical"

    def analyze_frame(self, interview_id: str, frame_b64: str) -> dict:
        state = self.sessions.get(interview_id)
        if not state:
            state = self.start_session(interview_id)

        state.frame_count += 1
        now = time.time()
        state.last_analysis_time = now

        result = {
            "face_detected": False,
            "face_count": 0,
            "eye_contact": 0,
            "gaze_direction": "Unknown",
            "head_pose": "Unknown",
            "deepfake_score": 85,
            "body_language": 50,
            "trust_score": state.last_trust_score,
            "risk_level": state.last_risk_level,
            "alerts": [],
            "emotion": "neutral",
            "emotion_scores": {},
            "pose_angles": {},
            "quality_score": 0,
            "looking_away_duration": 0.0,
            "looking_down_duration": 0.0,
            "timestamp": now,
        }

        try:
            face_result = state.face_analyzer.analyze(frame_b64)
            result["face_detected"] = face_result.face_count > 0
            result["face_count"] = face_result.face_count
            result["quality_score"] = round(face_result.confidence * 100, 1)
            result["pose_angles"] = face_result.pose_angles

            gaze = face_result.gaze_direction
            if gaze == "Unknown" and face_result.landmarks:
                gaze = self._estimate_gaze_direction(face_result.landmarks[0])
            result["gaze_direction"] = gaze
            result["head_pose"] = self._classify_head_pose(face_result.pose_angles)

            pitch = face_result.pose_angles.get("pitch", 0)
            yaw = face_result.pose_angles.get("yaw", 0)

            state.gaze_tracker.update(gaze, pitch, now)
            state.face_absent_tracker.update(face_result.face_count > 0, now)

            result["looking_away_duration"] = round(state.gaze_tracker.looking_away_total_sec, 1)
            result["looking_down_duration"] = round(state.gaze_tracker.looking_down_total_sec, 1)

            if face_result.landmarks:
                lm = face_result.landmarks[0]
                state.gaze_history.append(gaze)
                if len(state.gaze_history) > 100:
                    state.gaze_history = state.gaze_history[-100:]

                state.pose_history.append(face_result.pose_angles)
                if len(state.pose_history) > 100:
                    state.pose_history = state.pose_history[-100:]

                if face_result.gaze_yaw != 0.0:
                    state.gaze_yaw_history.append(face_result.gaze_yaw)
                    if len(state.gaze_yaw_history) > 100:
                        state.gaze_yaw_history = state.gaze_yaw_history[-100:]

            state.accumulated_scores["total_frames"] += 1

            if face_result.face_count == 0:
                state.accumulated_scores["face_absent_frames"] += 1
                absent_sec = now - state.face_absent_tracker.absent_since if state.face_absent_tracker.absent_since > 0 else 0
                if absent_sec > FACE_ABSENT_THRESHOLD_SEC and not state.face_absent_tracker.event_fired:
                    self._add_event(state, "face_disappearance", "high",
                                    f"Candidate face absent for {absent_sec:.0f}s", 0.9)
                    state.face_absent_tracker.event_fired = True
            else:
                state.accumulated_scores["face_present_frames"] += 1

            if face_result.face_count > 1:
                state.accumulated_scores["multiple_face_frames"] += 1
                if state.accumulated_scores["multiple_face_frames"] % 5 == 1:
                    self._add_event(state, "multiple_faces", "critical",
                                    f"Multiple faces detected: {face_result.face_count}", 0.95)

            if gaze == "Center":
                state.accumulated_scores["eye_contact_frames"] += 1
            elif gaze in ("Left", "Right"):
                state.accumulated_scores["looking_away_frames"] += 1

            if gaze in ("Left", "Right") and state.gaze_tracker.looking_away_total_sec >= LOOKING_AWAY_THRESHOLD_SEC:
                if not state.gaze_tracker.looking_away_event_fired:
                    duration = state.gaze_tracker.looking_away_total_sec
                    severity = "high" if duration >= 5.0 else "medium"
                    self._add_event(state, "looking_away_sustained", severity,
                                    f"Candidate looking {gaze.lower()} for {duration:.1f}s", 0.9)
                    state.gaze_tracker.looking_away_event_fired = True
                    state.accumulated_scores["sustained_looking_away_events"] += 1

            if pitch > 15:
                state.accumulated_scores["looking_down_frames"] += 1
                if state.gaze_tracker.looking_down_total_sec >= LOOKING_DOWN_THRESHOLD_SEC:
                    if not state.gaze_tracker.looking_down_event_fired:
                        self._add_event(state, "looking_down_sustained", "medium",
                                        f"Candidate looking down for {state.gaze_tracker.looking_down_total_sec:.1f}s", 0.8)
                        state.gaze_tracker.looking_down_event_fired = True
                        state.accumulated_scores["sustained_looking_down_events"] += 1

            state.face_count_history.append(face_result.face_count)
            if len(state.face_count_history) > 60:
                state.face_count_history = state.face_count_history[-60:]

            if len(state.pose_history) >= 5:
                recent = state.pose_history[-5:]
                yaw_std = np.std([p.get("yaw", 0) for p in recent])
                pitch_std = np.std([p.get("pitch", 0) for p in recent])
                if yaw_std > 10 or pitch_std > 10:
                    state.accumulated_scores["excessive_movement_frames"] += 1
                    if state.accumulated_scores["excessive_movement_frames"] % 6 == 1:
                        self._add_event(state, "excessive_movement", "medium",
                                        "Excessive head movement detected", 0.7)

            if face_result.occlusion_score < 0.3:
                state.accumulated_scores["occlusion_frames"] += 1
                if state.accumulated_scores["occlusion_frames"] % 10 == 1:
                    self._add_event(state, "face_occlusion", "medium",
                                    "Face partially occluded", 0.7)

            if face_result.blur_score < 0.3:
                if state.frame_count % 20 == 1:
                    self._add_event(state, "blurry_frame", "low",
                                    "Video quality degraded", 0.6)

            result["head_pose"] = self._classify_head_pose(face_result.pose_angles)

        except Exception as e:
            pass

        try:
            if state.frame_count % 5 == 0:
                deepfake_result = state.deepfake_detector.detect(frame_b64)
                df_score = deepfake_result.authenticity_score
                state.accumulated_scores["deepfake_scores"].append(df_score)
                if len(state.accumulated_scores["deepfake_scores"]) > 50:
                    state.accumulated_scores["deepfake_scores"] = state.accumulated_scores["deepfake_scores"][-50:]
                result["deepfake_score"] = round(df_score * 100, 1)

                if deepfake_result.is_deepfake:
                    self._add_event(state, "deepfake_suspicion", "critical",
                                    "Suspicious deepfake indicators detected", deepfake_result.confidence)
        except Exception:
            pass

        try:
            emotion_result = state.emotion_analyzer.analyze(frame_b64, state.emotion_history)
            result["emotion"] = emotion_result.dominant_emotion
            result["emotion_scores"] = emotion_result.emotion_scores

            state.emotion_history.append(emotion_result.emotion_scores)
            if len(state.emotion_history) > 30:
                state.emotion_history = state.emotion_history[-30:]

            state.accumulated_scores["emotion_scores"].append(emotion_result.consistency_score)
            if len(state.accumulated_scores["emotion_scores"]) > 50:
                state.accumulated_scores["emotion_scores"] = state.accumulated_scores["emotion_scores"][-50:]
        except Exception:
            pass

        result["eye_contact"] = self._compute_eye_contact_score(state)
        result["body_language"] = self._compute_body_language_score(state)

        trust = self._compute_trust_score(state)
        risk = self._determine_risk_level(trust)
        state.last_trust_score = trust
        state.last_risk_level = risk
        result["trust_score"] = trust
        result["risk_level"] = risk

        recent_events = state.events[-10:]
        result["alerts"] = [
            {
                "type": e.event_type,
                "severity": e.severity,
                "message": e.message,
                "confidence": e.confidence,
                "timestamp": e.timestamp,
            }
            for e in recent_events
        ]

        return result

    def add_client_event(self, interview_id: str, event_type: str, details: dict = None) -> dict:
        state = self.sessions.get(interview_id)
        if not state:
            return {"ok": False, "error": "No active session"}

        event = {
            "type": event_type,
            "timestamp": time.time(),
            "details": details or {},
        }
        state.client_events.append(event)

        if event_type == "tab_switch":
            self._add_event(state, "tab_switch", "high",
                            "Candidate switched browser tab", 0.95)
            state.accumulated_scores["looking_away_frames"] += 5
        elif event_type == "focus_loss":
            self._add_event(state, "window_unfocused", "medium",
                            "Candidate window lost focus", 0.85)
        elif event_type == "fullscreen_exit":
            self._add_event(state, "fullscreen_exit", "high",
                            "Candidate exited fullscreen mode", 0.9)
        elif event_type == "camera_disabled":
            self._add_event(state, "camera_disabled", "critical",
                            "Candidate disabled camera", 0.95)
        elif event_type == "mic_disabled":
            self._add_event(state, "mic_disabled", "high",
                            "Candidate disabled microphone", 0.85)
        elif event_type == "phone_detected":
            self._add_event(state, "phone_detected", "critical",
                            "Possible phone usage detected", 0.7)

        return {"ok": True}

    def get_analysis(self, interview_id: str) -> dict:
        state = self.sessions.get(interview_id)
        if not state or time.time() - state.last_analysis_time > 15:
            return {"active": False}

        return {
            "active": True,
            "face_detected": state.frame_count > 0 and state.accumulated_scores["face_present_frames"] > 0,
            "face_count": state.face_count_history[-1] if state.face_count_history else 0,
            "eye_contact": self._compute_eye_contact_score(state),
            "gaze_direction": state.gaze_history[-1] if state.gaze_history else "Unknown",
            "head_pose": self._classify_head_pose(state.pose_history[-1]) if state.pose_history else "Unknown",
            "mouse_score": 85,
            "tab_switches": sum(1 for e in state.client_events if e.get("type") == "tab_switch"),
            "deepfake_score": round(
                np.mean(state.accumulated_scores["deepfake_scores"]) * 100
                if state.accumulated_scores["deepfake_scores"] else 85, 1
            ),
            "body_language": self._compute_body_language_score(state),
            "trust_score": state.last_trust_score,
            "risk_level": state.last_risk_level,
            "emotion": state.emotion_history[-1] if state.emotion_history else {},
            "looking_away_duration": round(state.gaze_tracker.looking_away_total_sec, 1),
            "looking_down_duration": round(state.gaze_tracker.looking_down_total_sec, 1),
            "sustained_looking_away_events": state.accumulated_scores["sustained_looking_away_events"],
            "sustained_looking_down_events": state.accumulated_scores["sustained_looking_down_events"],
            "alerts": [
                {
                    "type": e.event_type,
                    "severity": e.severity,
                    "message": e.message,
                    "confidence": e.confidence,
                    "timestamp": e.timestamp,
                }
                for e in state.events[-15:]
            ],
            "frame_count": state.frame_count,
            "updated_at": state.last_analysis_time,
        }


live_analysis_service = LiveAnalysisService()
