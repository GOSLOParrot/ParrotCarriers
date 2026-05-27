using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace ParrotApp.VisualTools
{
    [DisallowMultipleComponent]
    public class VisualToolShutterBlackoutFeedback : MonoBehaviour
    {
        [SerializeField] private int sortingOrder = 89;
        [SerializeField] private float maxAlpha = 0.92f;
        [SerializeField] private float fadeInSeconds = 0.045f;
        [SerializeField] private float holdSeconds = 0.055f;
        [SerializeField] private float fadeOutSeconds = 0.16f;
        [SerializeField] private bool preserveShutterControlsArea = true;

        private Canvas _canvas;
        private RectTransform _blackoutRect;
        private Image _blackoutImage;
        private Coroutine _routine;

        public void Play()
        {
            EnsureUi();
            ApplyResponsiveLayout();
            if (_routine != null)
                StopCoroutine(_routine);
            _routine = StartCoroutine(BlackoutRoutine());
        }

        public void HideImmediate()
        {
            if (_routine != null)
            {
                StopCoroutine(_routine);
                _routine = null;
            }
            SetAlpha(0f);
            if (_canvas != null)
                _canvas.gameObject.SetActive(false);
        }

        private void EnsureUi()
        {
            if (_canvas != null)
                return;

            var root = new GameObject("VisualToolShutterBlackoutCanvas");
            root.transform.SetParent(transform, false);
            _canvas = root.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.overrideSorting = true;
            _canvas.sortingOrder = sortingOrder;

            var scaler = root.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = VisualToolHudMetrics.IqooNeo9LandscapeReferenceResolution;
            scaler.matchWidthOrHeight = 0.5f;

            var blackout = new GameObject("ViewfinderBlackout");
            blackout.transform.SetParent(root.transform, false);
            _blackoutRect = blackout.AddComponent<RectTransform>();
            _blackoutImage = blackout.AddComponent<Image>();
            _blackoutImage.color = new Color(0f, 0f, 0f, 0f);
            _blackoutImage.raycastTarget = false;
            _canvas.gameObject.SetActive(false);
        }

        private IEnumerator BlackoutRoutine()
        {
            if (_canvas == null || _blackoutImage == null)
                yield break;

            _canvas.gameObject.SetActive(true);
            yield return FadeAlpha(0f, maxAlpha, fadeInSeconds);
            if (holdSeconds > 0f)
                yield return new WaitForSecondsRealtime(holdSeconds);
            yield return FadeAlpha(maxAlpha, 0f, fadeOutSeconds);
            SetAlpha(0f);
            _canvas.gameObject.SetActive(false);
            _routine = null;
        }

        private IEnumerator FadeAlpha(float from, float to, float duration)
        {
            float safeDuration = Mathf.Max(0.001f, duration);
            float elapsed = 0f;
            while (elapsed < safeDuration)
            {
                elapsed += Time.unscaledDeltaTime;
                float t = Mathf.Clamp01(elapsed / safeDuration);
                SetAlpha(Mathf.Lerp(from, to, t));
                yield return null;
            }
            SetAlpha(to);
        }

        private void SetAlpha(float alpha)
        {
            if (_blackoutImage == null)
                return;
            _blackoutImage.color = new Color(0f, 0f, 0f, Mathf.Clamp01(alpha));
        }

        private void ApplyResponsiveLayout()
        {
            if (_blackoutRect == null)
                return;

            _blackoutRect.anchorMin = Vector2.zero;
            _blackoutRect.anchorMax = Vector2.one;
            _blackoutRect.pivot = new Vector2(0.5f, 0.5f);
            _blackoutRect.offsetMin = Vector2.zero;
            _blackoutRect.offsetMax = Vector2.zero;

            if (!preserveShutterControlsArea)
                return;

            if (Screen.width >= Screen.height)
            {
                _blackoutRect.offsetMax = new Vector2(
                    -VisualToolHudMetrics.RightSideShutterControlStripInset,
                    0f);
            }
            else
            {
                _blackoutRect.offsetMin = new Vector2(
                    0f,
                    VisualToolHudMetrics.BottomShutterControlStripInset);
            }
        }
    }
}
