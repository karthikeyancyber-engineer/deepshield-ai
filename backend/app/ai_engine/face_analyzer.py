import cv2
import numpy as np
import mediapipe as mp
from dataclasses import dataclass
from app.ai_engine.base import AIDetection, Timer, normalize, cosine_similarity


@dataclass
class FacialLandmarks:
    left_eye: tuple[float, float]
    right_eye: tuple[float, float]
    nose_tip: tuple[float, float]
    mouth_left: tuple[float, float]
    mouth_right: tuple[float, float]
    chin: tuple[float, float]
    left_eyebrow: tuple[float, float]
    right_eyebrow: tuple[float, float]
    left_iris: tuple[float, float] | None = None
    right_iris: tuple[float, float] | None = None


@dataclass
class FaceAnalysisResult:
    confidence: float
    face_count: int
    bounding_boxes: list[dict]
    landmarks: list[dict]
    quality_score: float
    symmetry_score: float
    blur_score: float
    illumination_score: float
    pose_angles: dict
    occlusion_score: float
    gaze_direction: str
    gaze_yaw: float
    explanations: list[dict]
    latency_ms: float


class FaceAnalyzer:
    """Real-time face detection and facial landmark analysis using MediaPipe."""

    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh

        self._face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5,
        )
        self._face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.LEFT_EYE_IDX = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387]
        self.RIGHT_EYE_IDX = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158]
        self.LEFT_EYE_CORNERS = [362, 133]
        self.RIGHT_EYE_CORNERS = [33, 263]
        self.LEFT_EYEBROW_IDX = [276, 283, 282, 295, 285]
        self.RIGHT_EYEBROW_IDX = [46, 53, 52, 65, 55]
        self.NOSE_TIP_IDX = 1
        self.MOUTH_LEFT_IDX = 61
        self.MOUTH_RIGHT_IDX = 291
        self.CHIN_IDX = 152
        self.LIPS_OUTER = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
        self.LEFT_IRIS_IDX = 468
        self.RIGHT_IRIS_IDX = 473

    def _decode_image(self, image_data: str) -> np.ndarray:
        import base64
        raw = base64.b64decode(image_data)
        arr = np.frombuffer(raw, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image data")
        return img

    def _compute_quality_metrics(self, image: np.ndarray, landmarks: np.ndarray) -> dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_normalized = normalize(blur_score, 0, 500)

        mean_brightness = np.mean(gray) / 255.0
        std_brightness = np.std(gray) / 255.0
        illumination_score = 1.0 - abs(mean_brightness - 0.5) * 2
        illumination_score = illumination_score * (1.0 - std_brightness * 0.3)

        left_eye = np.mean([landmarks[i] for i in self.LEFT_EYE_IDX], axis=0)[:2]
        right_eye = np.mean([landmarks[i] for i in self.RIGHT_EYE_IDX], axis=0)[:2]
        nose = landmarks[self.NOSE_TIP_IDX][:2]

        eye_dist = np.linalg.norm(right_eye - left_eye)
        nose_mid = (left_eye + right_eye) / 2
        symmetry_left = np.linalg.norm(nose - left_eye)
        symmetry_right = np.linalg.norm(nose - right_eye)
        symmetry_score = 1.0 - abs(symmetry_left - symmetry_right) / (eye_dist + 1e-8)
        symmetry_score = max(0.0, min(1.0, symmetry_score))

        face_width = eye_dist * 2.2
        face_height = np.linalg.norm(landmarks[self.CHIN_IDX][:2] - nose_mid) * 1.5
        face_region = gray[
            max(0, int(nose_mid[1] - face_height * 0.5)):min(h, int(nose_mid[1] + face_height * 0.5)),
            max(0, int(nose_mid[0] - face_width * 0.5)):min(w, int(nose_mid[0] + face_width * 0.5)),
        ]
        if face_region.size > 0:
            lbp_hist = self._compute_lbp_histogram(face_region)
            occlusion_score = float(np.sum(lbp_hist[:10]) / (np.sum(lbp_hist) + 1e-8))
            occlusion_score = 1.0 - occlusion_score
        else:
            occlusion_score = 0.5

        return {
            "blur": float(blur_normalized),
            "illumination": float(max(0.0, min(1.0, illumination_score))),
            "symmetry": float(symmetry_score),
            "occlusion": float(max(0.0, min(1.0, occlusion_score))),
        }

    def _compute_lbp_histogram(self, gray_region: np.ndarray) -> np.ndarray:
        h, w = gray_region.shape
        lbp = np.zeros((h - 2, w - 2), dtype=np.uint8)
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                center = gray_region[i, j]
                code = 0
                code |= (gray_region[i - 1, j - 1] >= center) << 7
                code |= (gray_region[i - 1, j] >= center) << 6
                code |= (gray_region[i - 1, j + 1] >= center) << 5
                code |= (gray_region[i, j + 1] >= center) << 4
                code |= (gray_region[i + 1, j + 1] >= center) << 3
                code |= (gray_region[i + 1, j] >= center) << 2
                code |= (gray_region[i + 1, j - 1] >= center) << 1
                code |= (gray_region[i, j - 1] >= center) << 0
                lbp[i - 1, j - 1] = code
        hist, _ = np.histogram(lbp, bins=256, range=(0, 256))
        return hist.astype(float)

    def _estimate_pose(self, landmarks: np.ndarray) -> dict:
        left_eye = np.mean([landmarks[i] for i in self.LEFT_EYE_IDX], axis=0)[:3]
        right_eye = np.mean([landmarks[i] for i in self.RIGHT_EYE_IDX], axis=0)[:3]
        nose = landmarks[self.NOSE_TIP_IDX][:3]
        chin = landmarks[self.CHIN_IDX][:3]

        eye_vec = right_eye - left_eye
        yaw = float(np.degrees(np.arctan2(eye_vec[2], eye_vec[0])))

        nose_to_eye = (left_eye + right_eye) / 2 - nose
        pitch = float(np.degrees(np.arctan2(nose_to_eye[1], np.linalg.norm(nose_to_eye[[0, 2]]))))

        vertical = chin[:2] - (left_eye[:2] + right_eye[:2]) / 2
        roll = float(np.degrees(np.arctan2(vertical[0], vertical[1])))

        return {"yaw": round(yaw, 2), "pitch": round(pitch, 2), "roll": round(roll, 2)}

    def _estimate_gaze_from_iris(self, landmarks: np.ndarray) -> tuple[str, float]:
        """Estimate gaze direction using iris center position relative to eye corners.

        Uses the iris landmarks (468 for left iris, 473 for right iris) which
        MediaPipe provides when refine_landmarks=True.

        Returns (direction_label, horizontal_offset_ratio).
        """
        left_iris = landmarks[self.LEFT_IRIS_IDX][:2]
        right_iris = landmarks[self.RIGHT_IRIS_IDX][:2]

        left_corner_inner = landmarks[self.LEFT_EYE_CORNERS[0]][:2]
        left_corner_outer = landmarks[self.LEFT_EYE_CORNERS[1]][:2]
        right_corner_inner = landmarks[self.RIGHT_EYE_CORNERS[0]][:2]
        right_corner_outer = landmarks[self.RIGHT_EYE_CORNERS[1]][:2]

        left_eye_width = np.linalg.norm(left_corner_outer - left_corner_inner)
        right_eye_width = np.linalg.norm(right_corner_outer - right_corner_inner)

        if left_eye_width < 1e-6 or right_eye_width < 1e-6:
            return "Unknown", 0.0

        left_iris_offset = np.linalg.norm(left_iris - left_corner_inner) / left_eye_width
        right_iris_offset = np.linalg.norm(right_iris - right_corner_inner) / right_eye_width

        avg_offset = (left_iris_offset + right_iris_offset) / 2.0

        normalized = (avg_offset - 0.5) * 2.0

        if normalized > 0.15:
            direction = "Right"
        elif normalized < -0.15:
            direction = "Left"
        else:
            direction = "Center"

        return direction, round(float(normalized), 4)

    def analyze(self, image_data: str) -> FaceAnalysisResult:
        with Timer() as timer:
            image = self._decode_image(image_data)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]

            detection_results = self._face_detection.process(rgb)
            mesh_results = self._face_mesh.process(rgb)

            bounding_boxes = []
            all_landmarks = []
            face_count = 0
            gaze_direction = "Unknown"
            gaze_yaw = 0.0

            if detection_results.detections:
                face_count = len(detection_results.detections)
                for det in detection_results.detections:
                    bb = det.location_data.relative_bounding_box
                    bounding_boxes.append({
                        "x": round(bb.xmin, 4),
                        "y": round(bb.ymin, 4),
                        "width": round(bb.width, 4),
                        "height": round(bb.height, 4),
                        "confidence": round(det.score[0], 4),
                    })

            quality = {"blur": 0.5, "illumination": 0.5, "symmetry": 0.5, "occlusion": 0.5}
            pose = {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}

            if mesh_results.multi_face_landmarks:
                face_lm = mesh_results.multi_face_landmarks[0]
                lm_array = np.array(
                    [[lm.x, lm.y, lm.z] for lm in face_lm.landmark]
                )

                left_eye = np.mean([lm_array[i] for i in self.LEFT_EYE_IDX], axis=0)[:2]
                right_eye = np.mean([lm_array[i] for i in self.RIGHT_EYE_IDX], axis=0)[:2]
                nose_tip = lm_array[self.NOSE_TIP_IDX][:2]
                mouth_l = lm_array[self.MOUTH_LEFT_IDX][:2]
                mouth_r = lm_array[self.MOUTH_RIGHT_IDX][:2]
                chin = lm_array[self.CHIN_IDX][:2]
                l_brow = np.mean([lm_array[i] for i in self.LEFT_EYEBROW_IDX], axis=0)[:2]
                r_brow = np.mean([lm_array[i] for i in self.RIGHT_EYEBROW_IDX], axis=0)[:2]

                left_iris = lm_array[self.LEFT_IRIS_IDX][:2]
                right_iris = lm_array[self.RIGHT_IRIS_IDX][:2]

                landmark_dict = {
                    "left_eye": {"x": round(float(left_eye[0]), 4), "y": round(float(left_eye[1]), 4)},
                    "right_eye": {"x": round(float(right_eye[0]), 4), "y": round(float(right_eye[1]), 4)},
                    "nose_tip": {"x": round(float(nose_tip[0]), 4), "y": round(float(nose_tip[1]), 4)},
                    "mouth_left": {"x": round(float(mouth_l[0]), 4), "y": round(float(mouth_l[1]), 4)},
                    "mouth_right": {"x": round(float(mouth_r[0]), 4), "y": round(float(mouth_r[1]), 4)},
                    "chin": {"x": round(float(chin[0]), 4), "y": round(float(chin[1]), 4)},
                    "left_eyebrow": {"x": round(float(l_brow[0]), 4), "y": round(float(l_brow[1]), 4)},
                    "right_eyebrow": {"x": round(float(r_brow[0]), 4), "y": round(float(r_brow[1]), 4)},
                    "left_iris": {"x": round(float(left_iris[0]), 4), "y": round(float(left_iris[1]), 4)},
                    "right_iris": {"x": round(float(right_iris[0]), 4), "y": round(float(right_iris[1]), 4)},
                }
                all_landmarks.append(landmark_dict)
                quality = self._compute_quality_metrics(image, lm_array)
                pose = self._estimate_pose(lm_array)
                gaze_direction, gaze_yaw = self._estimate_gaze_from_iris(lm_array)

            overall_quality = np.mean(list(quality.values()))
            confidence = round(float(overall_quality), 4)

            explanations = [
                {
                    "feature": "blur_score",
                    "value": quality["blur"],
                    "weight": 0.3,
                    "contribution": quality["blur"] * 0.3,
                    "explanation": f"Image sharpness: {quality['blur']:.1%} ({'Good' if quality['blur'] > 0.7 else 'Poor'})",
                },
                {
                    "feature": "illumination",
                    "value": quality["illumination"],
                    "weight": 0.2,
                    "contribution": quality["illumination"] * 0.2,
                    "explanation": f"Lighting quality: {quality['illumination']:.1%}",
                },
                {
                    "feature": "symmetry",
                    "value": quality["symmetry"],
                    "weight": 0.25,
                    "contribution": quality["symmetry"] * 0.25,
                    "explanation": f"Facial symmetry: {quality['symmetry']:.1%}",
                },
                {
                    "feature": "occlusion",
                    "value": quality["occlusion"],
                    "weight": 0.25,
                    "contribution": quality["occlusion"] * 0.25,
                    "explanation": f"Occlusion-free: {quality['occlusion']:.1%}",
                },
                {
                    "feature": "gaze",
                    "value": gaze_yaw,
                    "weight": 0.0,
                    "contribution": 0.0,
                    "explanation": f"Gaze direction: {gaze_direction} (offset: {gaze_yaw:.3f})",
                },
            ]

        return FaceAnalysisResult(
            confidence=confidence,
            face_count=face_count,
            bounding_boxes=bounding_boxes,
            landmarks=all_landmarks,
            quality_score=round(float(quality["blur"]), 4),
            symmetry_score=round(float(quality["symmetry"]), 4),
            blur_score=round(float(quality["blur"]), 4),
            illumination_score=round(float(quality["illumination"]), 4),
            pose_angles=pose,
            occlusion_score=round(float(quality["occlusion"]), 4),
            gaze_direction=gaze_direction,
            gaze_yaw=gaze_yaw,
            explanations=explanations,
            latency_ms=round(timer.elapsed_ms, 2),
        )
