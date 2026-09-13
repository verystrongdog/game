// 大脑视图（YANTF.BrainView）— 只读骨架的根：坐标口径 + 计数访问面
//
// 数值与口径来源：
//   design/presentation/visualization-3d/Unity接入设计.md §8.5
//     — 视图内部统一 **MNI 毫米**，根部施加**单一等比变换**（≈1/90）；网格与节点共用同一变换
//   §8.5 同时写明：§14.1 的 game_xyz 是**点位映射**（Z 除以 148.2，非等比），不得当作对网格的变换
//
// 资产轴映射（2026-09-13 直驱**实测统计判定**，不是推导）：
//   以 40 个载体的网格质心对 MNI 标签坐标做候选映射拟合，(−x, y, z) 的平均绝对误差 9.5 mm，
//   次优候选（含轴交换者）30 mm 以上 → 资产空间 = (−mni_X, mni_Y, mni_Z)，单位毫米。
//   含义：资产在 Unity 里是**躺着**的（Y 轴承载前后向、Z 轴承载上下向），故根部施加 **−90° X 旋转**。
//   FBX 导入的局部缩放实测为 100（Unity 对 Blender 单位的换算），与本节无关——根变换统一处理。
using System.Collections.Generic;
using UnityEngine;

namespace YANTF.BrainView
{
    /// <summary>只读骨架的根：持脑壳与链路容器，统一施加取向与缩放，并暴露计数供断言读取。</summary>
    [ExecuteAlways]      // 骨架的观感在 Edit 模式也要成立（场景未 Play 时也看得见脑）
    public class BrainViewRig : MonoBehaviour
    {
        /// <summary>脑壳不透明度（**呈现层取值，可调**）。
        /// 由来的事实：#143 烘焙件沿用了 v2 世代的逐脑叶 alpha=0.10，深色背景下近乎不可见；
        /// 而该材质是**导入资产的内嵌材质**，直接改它不持久（重导入即还原），故用
        /// MaterialPropertyBlock 在运行时覆盖，不碰资产。</summary>
        [SerializeField] private float shellAlpha = 0.35f;

        private MaterialPropertyBlock _mpb;
        [SerializeField] private Transform shell;
        [SerializeField] private Transform links;

        /// <summary>毫米 → 世界单位。1/90 使整脑约 1.9 世界单位高（Unity接入设计 §8.5）。</summary>
        public const float MmToWorld = 1f / 90f;

        /// <summary>脑壳区域对象数（= MeshFilter 数；期望等于 obj_file 去重后的载体数）。</summary>
        public int RegionCount { get; private set; }

        /// <summary>脑壳用到的共享材质数（期望等于实际用到的脑叶组数）。</summary>
        public int ShellMaterialCount { get; private set; }

        public Transform Shell => shell;
        public Transform Links => links;

        public void Bind(Transform shellRoot, Transform linkRoot)
        {
            shell = shellRoot;
            links = linkRoot;
            ApplyRootTransform();
            ApplyShellAlpha();
            Refresh();
        }

        private void OnEnable() => ApplyShellAlpha();

        /// <summary>按 <see cref="shellAlpha"/> 覆盖脑壳各 Renderer 的 _Color.a（不动资产）。</summary>
        public void ApplyShellAlpha()
        {
            if (shell == null) return;
            _mpb ??= new MaterialPropertyBlock();
            foreach (var r in shell.GetComponentsInChildren<MeshRenderer>(true))
            {
                var src = r.sharedMaterial;
                if (src == null || !src.HasProperty("_Color")) continue;
                var c = src.color;
                c.a = shellAlpha;
                r.GetPropertyBlock(_mpb);
                _mpb.SetColor("_Color", c);
                r.SetPropertyBlock(_mpb);
            }
        }

        /// <summary>根部取向与缩放：−90° X（资产躺着 → 立起）+ 等比 1/90。网格与链路共用。</summary>
        public void ApplyRootTransform()
        {
            transform.localRotation = Quaternion.Euler(-90f, 0f, 0f);
            transform.localScale = Vector3.one * MmToWorld;
        }

        /// <summary>重算计数（builder 与断言都读它，不各自数一遍）。</summary>
        public void Refresh()
        {
            RegionCount = 0;
            ShellMaterialCount = 0;
            if (shell == null) return;
            var materials = new HashSet<Material>();
            foreach (var mf in shell.GetComponentsInChildren<MeshFilter>(true))
            {
                if (mf.sharedMesh == null) continue;
                RegionCount++;
                var r = mf.GetComponent<MeshRenderer>();
                if (r == null) continue;
                foreach (var m in r.sharedMaterials) if (m != null) materials.Add(m);
            }
            ShellMaterialCount = materials.Count;
        }

        /// <summary>MNI 毫米 → 资产空间（实测映射；链路顶点与脑壳网格同空间）。</summary>
        public static Vector3 MniToAssetSpace(Vector3 mniMm)
        {
            return new Vector3(-mniMm.x, mniMm.y, mniMm.z);
        }
    }
}
