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

        [Tooltip("Emergency switch only. Keep false for demo parity so mobile uses the copied AR Mobile template ShaderGraph when it is supported.")]
        [SerializeField]
        bool m_ForceMobileMaterialFallback = false;

        [Tooltip("Android guard for copied ShaderGraph planes that resolve to an error shader. Root fix remains the demo2 ShaderGraph chain; this fallback is only a simple translucent white surface.")]
        [SerializeField]
        bool m_UseAndroidShaderGraphPlaneFallback = true;

        [Tooltip("Keep demo2's dot/surface material, but replace the AR/Occlusion slot on mobile if it renders as a visible error surface.")]
        [SerializeField]
        bool m_ReplaceMobileOcclusionSlot = true;

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
        string m_MaterialDebugSummary = "not_checked";
        static Material s_RuntimeSafePlaneMaterial;
        static Material s_RuntimeNoopOcclusionMaterial;

        public bool runtimeSafeMaterialActive => m_RuntimeSafeMaterialActive;
        public string materialDebugSummary => m_MaterialDebugSummary;

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
            if (m_PlaneMaterial != null && m_PlaneMaterial.HasProperty(m_ShaderAlphaPropertyID))
                m_PlaneMaterial.SetFloat(m_ShaderAlphaPropertyID, m_SurfaceVisualAlpha);
        }

        public void EnsureRuntimeSafeMaterialFallback()
        {
            if (!m_UseRuntimeSafeMaterialFallback || m_PlaneRenderer == null)
                return;

            var materials = m_PlaneRenderer.sharedMaterials;
            bool forceMobileFallback = m_ForceMobileMaterialFallback && Application.isMobilePlatform;
            if (materials == null || materials.Length == 0)
            {
                m_PlaneRenderer.sharedMaterials = new[] { RuntimeSafePlaneMaterial() };
                m_RuntimeSafeMaterialActive = true;
                m_MaterialDebugSummary = "fallback:no_materials";
                return;
            }

            var safe = RuntimeSafePlaneMaterial();
            var noopOcclusion = RuntimeNoopOcclusionMaterial();
            int count = Mathf.Max(1, materials.Length);
            var replacements = new Material[count];
            bool replacedAny = false;
            for (int i = 0; i < replacements.Length; i++)
            {
                var original = materials[i];
                if (ShouldReplaceOcclusionSlot(original))
                {
                    replacements[i] = noopOcclusion;
                    replacedAny = true;
                    continue;
                }

                // Prefer the copied AR Mobile demo2 ShaderGraph. If Android rejects
                // it, fall back to a simple translucent white surface while we fix the graph chain.
                if (forceMobileFallback || NeedsRuntimeSafeFallback(original) || NeedsAndroidPlaneShaderFallback(original))
                {
                    replacements[i] = safe;
                    replacedAny = true;
                }
                else
                {
                    replacements[i] = original;
                }
            }

            if (!replacedAny)
            {
                m_MaterialDebugSummary = "shader:" + MaterialShaderSummary(materials);
                return;
            }

            m_PlaneRenderer.sharedMaterials = replacements;
            m_RuntimeSafeMaterialActive = true;
            m_MaterialDebugSummary = "fallback:" + MaterialShaderSummary(materials);
        }

        bool ShouldReplaceOcclusionSlot(Material material)
        {
            if (!m_ReplaceMobileOcclusionSlot || material == null || material.shader == null)
                return false;

            string shaderName = material.shader.name ?? string.Empty;
            if (!shaderName.Equals("AR/Occlusion", System.StringComparison.Ordinal))
                return false;

            // The AR Mobile template occlusion slot should be visually invisible.
            // On the formal App Android build it can survive import but render as
            // a large error-colored surface. Keep the demo2 surface/dot material
            // and replace only this invisible helper slot.
            return Application.isMobilePlatform
                   || NeedsRuntimeSafeFallback(material)
                   || NeedsAndroidPlaneShaderFallback(material);
        }

        static bool NeedsRuntimeSafeFallback(Material material)
        {
            if (material == null || material.shader == null)
                return true;

            string shaderName = material.shader.name ?? string.Empty;
            return !material.shader.isSupported
                   || string.IsNullOrWhiteSpace(shaderName)
                   || shaderName.Contains("Hidden/InternalErrorShader")
                   || shaderName.Contains("Error");
        }

        bool NeedsAndroidPlaneShaderFallback(Material material)
        {
            if (!m_UseAndroidShaderGraphPlaneFallback)
                return false;

#if UNITY_ANDROID && !UNITY_EDITOR
            if (material == null || material.shader == null)
                return true;

            string shaderName = material.shader.name ?? string.Empty;
            return shaderName.Contains("Hidden/Shader Graph/FallbackError")
                   || shaderName.Contains("FallbackError");
#else
            return false;
#endif
        }

        static string MaterialShaderSummary(Material[] materials)
        {
            if (materials == null || materials.Length == 0)
                return "none";

            string result = "";
            for (int i = 0; i < materials.Length; i++)
            {
                if (i > 0)
                    result += "|";
                var material = materials[i];
                if (material == null)
                {
                    result += "null";
                    continue;
                }
                string shaderName = material.shader != null ? material.shader.name : "shader_null";
                result += string.IsNullOrWhiteSpace(shaderName) ? "shader_empty" : shaderName;
            }
            return result;
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
                name = "ParrotRuntimeSafeARPlaneTranslucentWhite",
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

            var tint = new Color(1f, 1f, 1f, 0.28f);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_BaseColor"))
                s_RuntimeSafePlaneMaterial.SetColor("_BaseColor", tint);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_Color"))
            {
                s_RuntimeSafePlaneMaterial.SetColor("_Color", tint);
                s_RuntimeSafePlaneMaterial.color = tint;
            }
            if (s_RuntimeSafePlaneMaterial.HasProperty("_Alpha"))
                s_RuntimeSafePlaneMaterial.SetFloat("_Alpha", 0.28f);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_PlaneAlpha"))
                s_RuntimeSafePlaneMaterial.SetFloat("_PlaneAlpha", 1f);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_PlaneOpacity"))
                s_RuntimeSafePlaneMaterial.SetFloat("_PlaneOpacity", 0.28f);
            if (s_RuntimeSafePlaneMaterial.HasProperty("_DotAlpha"))
                s_RuntimeSafePlaneMaterial.SetFloat("_DotAlpha", 0.28f);

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

        static Material RuntimeNoopOcclusionMaterial()
        {
            if (s_RuntimeNoopOcclusionMaterial != null)
                return s_RuntimeNoopOcclusionMaterial;

            var shader = Shader.Find("Universal Render Pipeline/Unlit")
                         ?? Shader.Find("Unlit/Transparent")
                         ?? Shader.Find("Sprites/Default")
                         ?? Shader.Find("Standard");
            s_RuntimeNoopOcclusionMaterial = new Material(shader)
            {
                name = "ParrotRuntimeNoopARPlaneOcclusion",
                renderQueue = (int)RenderQueue.Transparent,
            };

            var transparent = new Color(1f, 1f, 1f, 0f);
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_BaseColor"))
                s_RuntimeNoopOcclusionMaterial.SetColor("_BaseColor", transparent);
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_Color"))
            {
                s_RuntimeNoopOcclusionMaterial.SetColor("_Color", transparent);
                s_RuntimeNoopOcclusionMaterial.color = transparent;
            }
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_Alpha"))
                s_RuntimeNoopOcclusionMaterial.SetFloat("_Alpha", 0f);
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_Surface"))
                s_RuntimeNoopOcclusionMaterial.SetFloat("_Surface", 1f);
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_Blend"))
                s_RuntimeNoopOcclusionMaterial.SetFloat("_Blend", 0f);
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_SrcBlend"))
                s_RuntimeNoopOcclusionMaterial.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_DstBlend"))
                s_RuntimeNoopOcclusionMaterial.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            if (s_RuntimeNoopOcclusionMaterial.HasProperty("_ZWrite"))
                s_RuntimeNoopOcclusionMaterial.SetFloat("_ZWrite", 0f);
            s_RuntimeNoopOcclusionMaterial.EnableKeyword("_ALPHABLEND_ON");
            s_RuntimeNoopOcclusionMaterial.DisableKeyword("_ALPHATEST_ON");
            s_RuntimeNoopOcclusionMaterial.SetShaderPassEnabled("ShadowCaster", false);
            return s_RuntimeNoopOcclusionMaterial;
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
