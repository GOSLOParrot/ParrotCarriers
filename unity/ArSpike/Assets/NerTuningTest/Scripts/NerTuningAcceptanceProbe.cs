using System.Text;
using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.NerTuning
{
    /// <summary>
    /// Test-only acceptance probe for the Ner mouse tuning scene.
    /// It validates the same controller capabilities used by the mouse harness.
    /// </summary>
    public class NerTuningAcceptanceProbe : MonoBehaviour
    {
        [SerializeField] private bool runOnStart = true;
        [SerializeField] private Camera targetCamera;
        [SerializeField] private NerSpineController controller;
        [SerializeField] private Transform targetRoot;
        [SerializeField] private int minimumVisibleAttachments = 50;
        [SerializeField] private bool expectRightCheekHit = false;

        void Awake()
        {
            if (targetCamera == null) targetCamera = Camera.main;
            if (controller == null) controller = GetComponent<NerSpineController>();
            if (targetRoot == null) targetRoot = transform;
        }

        void Start()
        {
            if (runOnStart)
            {
                RunAcceptanceProbe();
            }
        }

        [ContextMenu("Run Acceptance Probe")]
        public void RunAcceptanceProbe()
        {
            var report = Probe();
            Debug.Log(report);
        }

        private string Probe()
        {
            var sb = new StringBuilder();
            bool hasFullSkin = HasFullNormalSkin(out var skinName, out var visibleAttachments);
            bool leftHit = RayHitsChild("NerTuningCheekHit_left");
            bool rightHit = RayHitsChild("NerTuningCheekHit_right");
            bool rightHitOk = !expectRightCheekHit || rightHit;
            bool facePatHit = RayHitsChild("NerTuningFacePatHit");
            bool bodyHit = RayHitsChild("NerTuningBodyHit");
            bool cheekOk = ProbeCheekCapabilities();
            bool patOk = ProbePatCapabilities();
            bool bodyOk = ProbeBodyCapabilities();
            bool walkOk = ProbeWalkCapability();
            bool scriptedGrabOk = ProbeScriptedGrab();
            bool pass = hasFullSkin && leftHit && rightHitOk && facePatHit && bodyHit && cheekOk && patOk && bodyOk && walkOk && scriptedGrabOk;

            sb.Append("[NerTuningAcceptanceProbe] ");
            sb.Append(pass ? "PASS" : "FAIL");
            sb.Append(" skin=");
            sb.Append(skinName);
            sb.Append(" visibleAttachments=");
            sb.Append(visibleAttachments);
            sb.Append(" hits(left/right/facePat/body)=");
            sb.Append(leftHit);
            sb.Append("/");
            sb.Append(rightHit);
            sb.Append("/");
            sb.Append(facePatHit);
            sb.Append("/");
            sb.Append(bodyHit);
            sb.Append(" rightExpected=");
            sb.Append(expectRightCheekHit);
            sb.Append(" caps(cheek/pat/body/walk)=");
            sb.Append(cheekOk);
            sb.Append("/");
            sb.Append(patOk);
            sb.Append("/");
            sb.Append(bodyOk);
            sb.Append("/");
            sb.Append(walkOk);
            sb.Append(" scriptedGrab=");
            sb.Append(scriptedGrabOk);
            return sb.ToString();
        }

        private bool HasFullNormalSkin(out string skinName, out int visibleAttachments)
        {
            skinName = "missing";
            visibleAttachments = 0;
            var skeletonAnimation = GetComponent<Spine.Unity.SkeletonAnimation>();
            if (skeletonAnimation == null) return false;

            skeletonAnimation.Initialize(false, true);
            var skeleton = skeletonAnimation.Skeleton;
            if (skeleton == null) return false;
            skinName = skeleton.Skin != null ? skeleton.Skin.Name : "null";

            for (int i = 0; i < skeleton.Slots.Count; i++)
            {
                if (skeleton.Slots.Items[i].Attachment != null) visibleAttachments++;
            }

            return skinName == "Normal" && visibleAttachments >= minimumVisibleAttachments;
        }

        private bool RayHitsChild(string childName)
        {
            if (targetCamera == null) targetCamera = Camera.main;
            if (targetCamera == null) return false;

            var child = transform.Find(childName);
            if (child == null) return false;
            var targetCollider = child.GetComponent<Collider>();
            if (targetCollider == null) return false;

            Vector3 screen = targetCamera.WorldToScreenPoint(targetCollider.bounds.center);
            var ray = targetCamera.ScreenPointToRay(new Vector2(screen.x, screen.y));
            var hits = Physics.RaycastAll(ray, 8f, ~0, QueryTriggerInteraction.Collide);
            for (int i = 0; i < hits.Length; i++)
            {
                if (hits[i].collider == targetCollider) return true;
            }
            return false;
        }

        private bool ProbeCheekCapabilities()
        {
            if (controller == null) return false;
            bool start = controller.ApplyCapability(
                "cheek_pinch_start",
                "{\"side\":\"left\",\"strength\":0.2,\"drag_x\":-0.4,\"drag_y\":0.0}");
            bool hold = controller.ApplyCapability(
                "cheek_pinch_hold",
                "{\"side\":\"left\",\"strength\":0.7,\"drag_x\":-0.9,\"drag_y\":0.15}");
            bool warning = controller.ApplyCapability(
                "cheek_pinch_warning",
                "{\"side\":\"left\",\"strength\":0.8,\"drag_x\":-1.0,\"drag_y\":0.2}");
            bool release = controller.ApplyCapability(
                "cheek_pinch_release",
                "{\"side\":\"left\",\"strength\":0,\"drag_x\":0,\"drag_y\":0}");
            return start && hold && warning && release;
        }

        private bool ProbePatCapabilities()
        {
            if (controller == null) return false;
            bool start = controller.ApplyCapability("pat_idle", "{}");
            bool end = controller.ApplyCapability("pat_end", "{}");
            return start && end;
        }

        private bool ProbeBodyCapabilities()
        {
            if (controller == null) return false;
            bool start = controller.ApplyCapability(
                "body_pickup_start",
                "{\"state\":\"body_pickup_start\",\"held_seconds\":0,\"lift_m\":0.095,\"drag_speed\":0,\"ground_x\":0,\"ground_y\":0,\"ground_z\":0}");
            bool held = controller.ApplyCapability(
                "body_held_in_air",
                "{\"state\":\"body_held_in_air\",\"held_seconds\":0.4,\"lift_m\":0.095,\"drag_speed\":0,\"ground_x\":0,\"ground_y\":0,\"ground_z\":0}");
            bool dragging = controller.ApplyCapability(
                "body_dragging_in_air",
                "{\"state\":\"body_dragging_in_air\",\"held_seconds\":0.7,\"lift_m\":0.095,\"drag_speed\":0.55,\"ground_x\":0.12,\"ground_y\":0,\"ground_z\":0.12}");
            bool release = controller.ApplyCapability(
                "body_place_release",
                "{\"state\":\"body_place_release\",\"held_seconds\":0.9,\"lift_m\":0.095,\"drag_speed\":0,\"ground_x\":0.12,\"ground_y\":0,\"ground_z\":0.12}");
            return start && held && dragging && release;
        }

        private bool ProbeWalkCapability()
        {
            if (controller == null || targetRoot == null) return false;
            Vector3 before = targetRoot.position;
            bool walked = controller.ApplyCapability(
                "spine_walk",
                "{\"x\":1,\"y\":0,\"z\":0,\"deltaTime\":0.16}");
            bool moved = Vector3.Distance(before, targetRoot.position) > 0.01f;
            targetRoot.position = before;
            controller.ApplyCapability("spine_idle", "{}");
            return walked && moved;
        }

        private bool ProbeScriptedGrab()
        {
            var harness = GetComponent<NerMouseTuningHarness>();
            return harness != null && harness.RunScriptedPickupDropProbe();
        }
    }
}
