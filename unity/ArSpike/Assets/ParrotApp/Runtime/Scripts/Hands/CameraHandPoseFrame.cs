using UnityEngine;

namespace ParrotApp.Hands
{
    public struct CameraHandPoseFrame
    {
        public bool HandDetected;
        public bool HasFingerJoints;
        public bool IsRightHand;
        public string Source;
        public string Status;
        public float Confidence;
        public float EstimatedDepthMeters;

        public Vector3 WristPosition;
        public Vector3 PalmPosition;
        public Vector3 PalmNormal;

        public Vector3 IndexProximal;
        public Vector3 IndexIntermediate;
        public Vector3 IndexDistal;
        public Vector3 IndexTip;

        public Vector3 MiddleProximal;
        public Vector3 MiddleIntermediate;
        public Vector3 MiddleTip;

        public Vector3 RingProximal;
        public Vector3 RingIntermediate;
        public Vector3 RingTip;

        public Vector3 LittleProximal;
        public Vector3 LittleIntermediate;
        public Vector3 LittleTip;

        public HandPerchPose PerchPose;

        public static CameraHandPoseFrame Lost(string source, string status)
        {
            return new CameraHandPoseFrame
            {
                HandDetected = false,
                Source = string.IsNullOrWhiteSpace(source) ? "camera_cv" : source,
                Status = string.IsNullOrWhiteSpace(status) ? "hand_lost" : status,
            };
        }
    }
}
