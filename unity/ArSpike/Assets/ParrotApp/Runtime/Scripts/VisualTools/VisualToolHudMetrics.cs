using UnityEngine;

namespace ParrotApp.VisualTools
{
    public static class VisualToolHudMetrics
    {
        public static readonly Vector2 IqooNeo9LandscapeReferenceResolution = new Vector2(2800f, 1260f);
        public static readonly Vector2 BottomShutterPosition = new Vector2(0f, 42f);
        public static readonly Vector2 RightSideShutterPosition = new Vector2(-42f, 0f);
        public static readonly Vector2 BottomShutterSize = new Vector2(112f, 112f);
        public static readonly Vector2 ShutterFeedbackSize = new Vector2(160f, 42f);
        public static readonly Vector2 BottomShutterFeedbackPosition = new Vector2(0f, 164f);
        public static readonly Vector2 RightSideShutterFeedbackPosition = new Vector2(-184f, 0f);
        public static readonly float BottomShutterControlStripInset = 210f;
        public static readonly float RightSideShutterControlStripInset = 180f;

        public static VisualToolRegion DefaultBBoxRegion =>
            VisualToolRegion.ScreenNormalized(0.36f, 0.28f, 0.28f, 0.24f);

        public static VisualToolRegion DefaultMagnifierRegion =>
            VisualToolRegion.ScreenNormalized(0.41f, 0.14f, 0.18f, 0.48f);

        public static void ApplyResponsiveShutterLayout(RectTransform shutter)
        {
            if (shutter == null)
                return;

            bool landscape = Screen.width >= Screen.height;
            Vector2 anchor = landscape ? new Vector2(1f, 0.5f) : new Vector2(0.5f, 0f);
            shutter.anchorMin = anchor;
            shutter.anchorMax = anchor;
            shutter.pivot = anchor;
            shutter.anchoredPosition = landscape ? RightSideShutterPosition : BottomShutterPosition;
            shutter.sizeDelta = BottomShutterSize;
        }

        public static void ApplyResponsiveShutterFeedbackLayout(RectTransform feedback)
        {
            if (feedback == null)
                return;

            bool landscape = Screen.width >= Screen.height;
            Vector2 anchor = landscape ? new Vector2(1f, 0.5f) : new Vector2(0.5f, 0f);
            feedback.anchorMin = anchor;
            feedback.anchorMax = anchor;
            feedback.pivot = anchor;
            feedback.anchoredPosition = landscape ? RightSideShutterFeedbackPosition : BottomShutterFeedbackPosition;
            feedback.sizeDelta = ShutterFeedbackSize;
        }
    }
}
