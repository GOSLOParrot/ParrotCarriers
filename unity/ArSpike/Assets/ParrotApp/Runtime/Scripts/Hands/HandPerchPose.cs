using UnityEngine;

namespace ParrotApp.Hands
{
    public struct HandPerchPose
    {
        public bool IsValid;
        public Vector3 Position;
        public Quaternion Rotation;
        public Vector3 FingerDirection;
        public Vector3 PalmPosition;
        public Vector3 PalmNormal;
        public Vector3 FacingDirection;
        public float Confidence;
        public string Source;

        public Vector3 ToRootPosition(Vector3 footAnchorLocalOffset, Vector3 rootClearanceLocalOffset)
        {
            return Position - (Rotation * footAnchorLocalOffset) + (Rotation * rootClearanceLocalOffset);
        }
    }
}
