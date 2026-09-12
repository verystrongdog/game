// 玫瑰花海实例化材质着色器（Grilling #126）
// 用途：Graphics.DrawMeshInstanced 一次绘制全部 ~4500 株玫瑰。
// 要点：① multi_compile_instancing 开启实例化；② Cull Off 实现叶/瓣单面几何双面可见；
//       ③ 顶点色承载茎/叶/花三色 → 单 draw call 内区分部位。
// 注：Lambert 光照模型下背面法线朝外 → 背面偏暗，为已知简化（见 unity/README.md §二·F）。
Shader "YANTF/RoseInstanced"
{
    Properties
    {
        _Tint ("Tint", Color) = (1,1,1,1)
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }
        Cull Off
        LOD 200

        CGPROGRAM
        #pragma surface surf Lambert
        #pragma multi_compile_instancing
        #pragma target 3.0

        fixed4 _Tint;

        struct Input
        {
            float4 color : COLOR;
        };

        void surf(Input IN, inout SurfaceOutput o)
        {
            o.Albedo = IN.color.rgb * _Tint.rgb;
            o.Alpha = 1.0;
        }
        ENDCG
    }

    FallBack "Diffuse"
}
