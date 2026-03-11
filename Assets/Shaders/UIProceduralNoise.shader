Shader "Custom/UIProceduralNoise"
{
    Properties
    {
        [PerRendererData] _MainTex ("Sprite Texture", 2D) = "white" {}
        _GlobalAlpha ("Global Alpha", Range(0, 1)) = 0.0
    }
    SubShader
    {
        Tags
        {
            "Queue"="Transparent"
            "IgnoreProjector"="True"
            "RenderType"="Transparent"
            "PreviewType"="Plane"
            "CanUseSpriteAtlas"="True"
        }

        Stencil
        {
            Ref 0
            Comp Always
            Pass Keep
        }

        Cull Off
        Lighting Off
        ZWrite Off
        ZTest [unity_GUIZTestMode]
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 2.0

            #include "UnityCG.cginc"
            #include "UnityUI.cginc"

            struct appdata_t
            {
                float4 vertex   : POSITION;
                float4 color    : COLOR;
                float2 texcoord : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct v2f
            {
                float4 vertex   : SV_POSITION;
                fixed4 color    : COLOR;
                float2 texcoord  : TEXCOORD0;
                float4 worldPosition : TEXCOORD1;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            sampler2D _MainTex;
            fixed4 _TextureSampleAdd;
            float4 _ClipRect;
            float _GlobalAlpha;

            v2f vert(appdata_t v)
            {
                v2f OUT;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(OUT);
                OUT.worldPosition = v.vertex;
                OUT.vertex = UnityObjectToClipPos(OUT.worldPosition);

                OUT.texcoord = v.texcoord;

                OUT.color = v.color;
                return OUT;
            }

            // pixel noise hash func
            float hash(float2 p)
            {
                float dt = dot(p, float2(12.9898, 78.233));
                float sn = sin(dt);
                return frac(sn * 43758.5453);
            }

            fixed4 frag(v2f IN) : SV_Target
            {
                // based on uv coord and time
                float2 uv = IN.texcoord;
                
                // pixelate to match 256x256
                float resolution = 256.0;
                uv = floor(uv * resolution) / resolution;

                float noiseVal = hash(uv + _Time.y * 10.0); // fast static flicker

                half4 color = half4(noiseVal, noiseVal, noiseVal, _GlobalAlpha);

                // ui masking
                #ifdef UNITY_UI_CLIP_RECT
                color.a *= UnityGet2DClipping(IN.worldPosition.xy, _ClipRect);
                #endif

                // clip if alpha is close to 0
                clip (color.a - 0.001);

                return color;
            }
            ENDCG
        }
    }
}
