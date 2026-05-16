using UnityEngine.Rendering;
using UnityEngine.XR.Interaction.Toolkit.Utilities.Tweenables.Primitives;

namespace UnityEngine.XR.Interaction.Toolkit.Samples.ARStarterAssets
{
    /// <summary>
    /// Performs additional visual operations on the ARFeatheredPlane mesh, such as animated alpha fading.
    /// </summary>
    [RequireComponent(typeof(MeshRenderer))]
    public class ARFeatheredPlaneMeshVisualizerCompanion : MonoBehaviour
    {
        [Tooltip("Renderer component on the ARFeatheredPlane prefab. Used to fetch the material to fade in/out.")]
        [SerializeField]
        Renderer m_PlaneRenderer;

        [SerializeField]
        bool m_UseRuntimeSafeMaterialFallback = true;

        /// <summary>
        /// The Renderer component on the ARFeatheredPlane prefab. Used to fetch the material to fade in/out.
        /// </summary>
        public Renderer planeRenderer
        {
            get => m_PlaneRenderer;
            set => m_PlaneRenderer = value;
        }

        [Tooltip("Fade in/out speed multiplier applied during the alpha tweening. The lower the value, the slower it works. A value of 1 is full speed (1 second).")]
        [Range(0.1f, 1.0f)]
        [SerializeField]
        float m_FadeSpeed = 1f;

        /// <summary>
        /// Fade in/out speed multiplier applied during the alpha tweening.
        /// The lower the value, the slower it works. A value of 1 is full speed (1 second).
        /// </summary>
        public float fadeSpeed
        {
            get => m_FadeSpeed;
            set => m_FadeSpeed = value;
        }

        int m_ShaderAlphaPropertyID;
        float m_SurfaceVisualAlpha = 1f;
        float m_TweenProgress;
        Material m_PlaneMaterial;
        bool m_RuntimeSafeMaterialActive;
        static Material s_RuntimeSafePlaneMaterial;

#pragma warning disable CS0618 // Type or member is obsolete -- affordance system to be replaced in a future XRI version
        readonly FloatTweenableVariable m_AlphaTweenableVariable = new FloatTweenableVariable();
#pragma warning restore CS0618

        /// <summary>
        /// See <see cref="MonoBehaviour"/>.
        /// </summary>
        void Awake()
        {
            m_ShaderAlphaPropertyID = Shader.PropertyToID("_PlaneAlpha");
            if (m_PlaneRenderer == null)
                m_PlaneRenderer = GetComponent<Renderer>();
            if (m_PlaneRenderer == null)
                return;
            EnsureRuntimeSafeMaterialFallback();
            m_PlaneMaterial = m_PlaneRenderer.material;
            visualizeSurfaces = true;
        }

        /// <summary>
        /// See <see cref="MonoBehaviour"/>.
        /// </summary>
        void OnDestroy()
        {
            m_AlphaTweenableVariable.Dispose();
        }

        /// <summary>
        /// See <see cref="MonoBehaviour"/>.
        /// </summary>
        void Update()
        {
            m_AlphaTweenableVariable.HandleTween(m_TweenProgress);
            m_TweenProgress += Time.unscaledDeltaTime * m_FadeSpeed;
            m_SurfaceVisualAlpha = m_AlphaTweenableVariable.Value;
            if (!m_RuntimeSafeMaterialActive && m_PlaneMaterial != null)
                m_PlaneMaterial.SetFloat(m_ShaderAlphaPropertyID, m_SurfaceVisualAlpha);
        }

        public void EnsureRuntimeSafeMaterialFallback()
        {
            if (!m_UseRuntimeSafeMaterialFallback || m_PlaneRenderer == null)
                return;

            var materials = m_PlaneRenderer.sharedMaterials;
            bool forceMobileFallback = Application.isMobilePlatform;
            bool needsFallback = forceMobileFallback || materials == null || materials.Length == 0;
            if (!needsFallback && materials != null)
            {
                for (int i = 0; i < materials.Length; i++)
                {
                    if (NeedsRuntimeSafeFallback(materials[i]))
                    {
                        needsFallback = true;
                        break;
                    }
                }
            }

            if (!needsFallback)
                return;

            var safe = RuntimeSafePlaneMaterial();
            int count = Mathf.Max(1, materials != null ? materials.Length : 1);
            var replacements = new Material[count];
            for (int i = 0; i < replacements.Length; i++)
                replacements[i] = safe;
            m_PlaneRenderer.sharedMaterials = replacements;
            m_RuntimeSafeMaterialActive = true;
        }

        static bool NeedsRuntimeSafeFallback(Material material)
        {
            if (material == null || material.shader == null)
                return true;

            string shaderName = material.shader.name;
            return !material.shader.isSupported
                   || string.IsNullOrWhiteSpace(shaderName)
                   || shaderName.Contains("Hidden/InternalErrorShader")
                   || shaderName.Contains("Error");
        }

        static Material RuntimeSafePlaneMaterial()
        {
            if (s_RuntimeSafePlaneMaterial != null)
                return s_RuntimeSafePlaneMaterial;

            var shader = Shader.Find("Universal Render Pipeline/Unlit")
                         ?? Shader.Find("Unlit/Transparent")
                         ?? Shader.Find("Sprites/Default")
                         ?? Shader.Find("Standard");
            s_RuntimeSafePlaneMaterial = new Material(shader)
            {
                name = "ParrotRuntimeSafeARPlaneDots",
                renderQueue = (int)RenderQueue.Transparent,
            };

            var texture = Resources.Load<Texture2D>("ARMobileTemplate/Textures/PlanePatternDot");
            if (texture != null)
            {
                if (s_RuntimeSafePlaneMaterial.HasProperty("_BaseMap"))
                    s_RuntimeSafePlaneMaterial.SetTexture("_BaseMap", texture);
                if (s_RuntimeSafePlaneMaterial.HasProperty("_MainTex"))
                    s_RuntimeSafePlaneMaterial.SetTexture("_MainTex", texture);
            }

            var tint = new Color(1f, 1f, 1f, 0.88f);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_BaseColor"))
                s_RuntimeSafePlaneMaterial.SetColor("_BaseColor", tint);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_Color"))
            {
                s_RuntimeSafePlaneMaterial.SetColor("_Color", tint);
                s_RuntimeSafePlaneMaterial.color = tint;
            }

            if (s_RuntimeSafePlaneMaterial.HasProperty("_Surface"))
                s_RuntimeSafePlaneMaterial.SetFloat("_Surface", 1f);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_Blend"))
                s_RuntimeSafePlaneMaterial.SetFloat("_Blend", 0f);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_SrcBlend"))
                s_RuntimeSafePlaneMaterial.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_DstBlend"))
                s_RuntimeSafePlaneMaterial.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_ZWrite"))
                s_RuntimeSafePlaneMaterial.SetFloat("_ZWrite", 0f);
            s_RuntimeSafePlaneMaterial.EnableKeyword("_ALPHABLEND_ON");
            s_RuntimeSafePlaneMaterial.DisableKeyword("_ALPHATEST_ON");
            s_RuntimeSafePlaneMaterial.SetShaderPassEnabled("ShadowCaster", false);
            return s_RuntimeSafePlaneMaterial;
        }

        /// <summary>
        /// Show plane surfaces if true, hide plane surfaces if false
        /// </summary>
        public bool visualizeSurfaces
        {
            set
            {
                m_TweenProgress = 0f;
                m_AlphaTweenableVariable.target = value ? 1f : 0f;
                m_AlphaTweenableVariable.HandleTween(0f);
            }
        }
    }
}
