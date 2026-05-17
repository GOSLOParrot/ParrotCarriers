Shader "Parrot/ARPlaneFallbackTransparent"
{
    Properties
    {
        _MainTex ("Plane Pattern", 2D) = "white" {}
        _Color ("Tint", Color) = (1, 1, 1, 0.28)
        _Alpha ("Alpha", Range(0, 1)) = 0.28
        _PlaneAlpha ("Plane Fade", Range(0, 1)) = 1
    }

    SubShader
    {
        Tags
        {
            "Queue" = "Transparent"
            "RenderType" = "Transparent"
            "IgnoreProjector" = "True"
        }
        LOD 100
        Cull Off
        Lighting Off
        ZWrite Off
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 2.0
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            sampler2D _MainTex;
            float4 _MainTex_ST;
            fixed4 _Color;
            float _Alpha;
            float _PlaneAlpha;

            v2f vert(appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                fixed4 tex = tex2D(_MainTex, i.uv);
                fixed4 col = _Color;
                col.rgb *= tex.rgb;
                col.a *= tex.a * _Alpha * _PlaneAlpha;
                return col;
            }
            ENDCG
        }
    }

    Fallback Off
}
