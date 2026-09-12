// 白盒人形 + 程序化动作（Grilling #122 Q4/Q5：暂无外部模型，白盒占位；
// 外部人形模型接入时以同类接口替换本类，驱动层不变）。
// 仅用 Unity 图元（Capsule/Sphere）拼装，零外部资产；动作由骨骼 transform 程序化驱动。
using UnityEngine;

namespace YANTF.Demo
{
    public sealed class CharacterVisual : MonoBehaviour
    {
        private enum AnimKind { Idle, Walk, PhysicalAttack, MentalAttack, Defend, HitReaction, Down }

        // ---- 骨骼引用（由 BuildWhitebox 建立）----
        private Transform _root;    // 髋部（整体朝向/倒地旋转用）
        private Transform _torso;
        private Transform _head;
        private Transform _armL;
        private Transform _armR;
        private Transform _legL;
        private Transform _legR;

        private AnimKind _kind = AnimKind.Idle;
        private float _animT;             // 当前动作进度
        private float _walkSpeed;         // 0..1
        private float _defendActive;
        private Color _tint = new Color(0.8f, 0.8f, 0.85f, 1f);

        private static readonly Quaternion IdleArmL = Quaternion.Euler(4f, 0f, -6f);
        private static readonly Quaternion IdleArmR = Quaternion.Euler(4f, 0f, 6f);
        private static readonly Quaternion IdleLeg  = Quaternion.identity;

        public void BuildWhitebox(Color tint)
        {
            _tint = tint;
            foreach (Transform child in transform) Destroy(child.gameObject);

            // 尺寸：总高 ~1.8m（医院层高 3.6m 比例参考），单位米
            float hipH = 0.95f;
            var mat = MakeMat(tint);

            _root = new GameObject("hips").transform;
            _root.SetParent(transform, false);
            _root.localPosition = new Vector3(0f, hipH, 0f);

            _torso = MakePrimitive(PrimitiveType.Capsule, "torso", mat, new Vector3(0.34f, 0.42f, 0.2f));
            _torso.SetParent(_root, false);
            _torso.localPosition = new Vector3(0f, 0.32f, 0f);

            _head = MakePrimitive(PrimitiveType.Sphere, "head", MakeMat(Lighten(tint, 0.15f)), Vector3.one * 0.2f);
            _head.SetParent(_root, false);
            _head.localPosition = new Vector3(0f, 0.95f, 0f);

            // 上肢：单段胶囊，肩部为枢轴
            _armR = MakePrimitive(PrimitiveType.Capsule, "armR", mat, new Vector3(0.09f, 0.35f, 0.09f));
            _armR.SetParent(_root, false);
            _armR.localPosition = new Vector3(0.26f, 0.78f, 0f);

            _armL = MakePrimitive(PrimitiveType.Capsule, "armL", mat, new Vector3(0.09f, 0.35f, 0.09f));
            _armL.SetParent(_root, false);
            _armL.localPosition = new Vector3(-0.26f, 0.78f, 0f);

            // 下肢：以髋为枢轴
            _legR = MakePrimitive(PrimitiveType.Capsule, "legR", mat, new Vector3(0.1f, 0.42f, 0.1f));
            _legR.SetParent(_root, false);
            _legR.localPosition = new Vector3(0.11f, -0.4f, 0f);

            _legL = MakePrimitive(PrimitiveType.Capsule, "legL", mat, new Vector3(0.1f, 0.42f, 0.1f));
            _legL.SetParent(_root, false);
            _legL.localPosition = new Vector3(-0.11f, -0.4f, 0f);

            ApplyPose(Quaternion.identity, IdleArmL, IdleArmR, IdleLeg, IdleLeg);
        }

        // ---- 对外动作接口（外部模型接入时替换内部实现即可）----
        public void PlayIdle()          { _kind = AnimKind.Idle; }
        public void PlayWalk(float s)   { _walkSpeed = Mathf.Clamp01(s); if (_kind != AnimKind.Walk && _walkSpeed > 0.01f) _kind = AnimKind.Walk; }
        public void PlayPhysicalAttack(){ _kind = AnimKind.PhysicalAttack; _animT = 0f; }
        public void PlayMentalAttack()  { _kind = AnimKind.MentalAttack; _animT = 0f; }
        public void PlayDefend(bool on) { _defendActive = on ? 1f : 0f; if (on && _kind == AnimKind.Idle) _kind = AnimKind.Defend; if (!on && _kind == AnimKind.Defend) _kind = AnimKind.Idle; }
        public void PlayHitReaction()   { if (_kind != AnimKind.Down) { _kind = AnimKind.HitReaction; _animT = 0f; } }
        public void PlayDown()          { _kind = AnimKind.Down; _animT = 0f; }

        private void Update()
        {
            if (_root == null) return;
            float dt = Time.deltaTime;
            _animT += dt;

            Quaternion body = Quaternion.identity;
            Quaternion aL = IdleArmL, aR = IdleArmR, lL = IdleLeg, lR = IdleLeg;
            float breathe = Mathf.Sin(Time.time * 2.2f) * 0.6f;

            switch (_kind)
            {
                case AnimKind.Walk:
                {
                    float ph = Time.time * (6f + 6f * _walkSpeed);
                    float amp = 0.5f * _walkSpeed;
                    body = Quaternion.Euler(0f, 0f, Mathf.Sin(ph) * 2f * _walkSpeed);
                    aL = Quaternion.Euler(20f * amp * Mathf.Sin(ph), 0f, -6f);
                    aR = Quaternion.Euler(20f * amp * Mathf.Sin(ph + Mathf.PI), 0f, 6f);
                    lL = Quaternion.Euler(-35f * amp * Mathf.Sin(ph), 0f, 0f);
                    lR = Quaternion.Euler(-35f * amp * Mathf.Sin(ph + Mathf.PI), 0f, 0f);
                    if (_walkSpeed <= 0.01f) _kind = AnimKind.Idle;
                    break;
                }
                case AnimKind.PhysicalAttack:
                {
                    // 右臂从后上挥向前下（0.32s 击出 → 0.15s 回摆）
                    float t = _animT;
                    if (t < 0.32f)
                    {
                        float k = t / 0.32f;
                        aR = Quaternion.Euler(-120f * k + 30f, 0f, 40f * (1f - k));
                        body = Quaternion.Euler(0f, 0f, -10f * k);
                    }
                    else if (t < 0.47f)
                    {
                        aR = Quaternion.Euler(-90f, 0f, 0f);
                        body = Quaternion.identity;
                    }
                    else { _kind = AnimKind.Idle; }
                    break;
                }
                case AnimKind.MentalAttack:
                {
                    float t = _animT;
                    if (t < 0.35f)
                    {
                        float k = t / 0.35f;
                        aR = Quaternion.Euler(-160f * k, 0f, -20f * k);   // 抬臂前指
                    }
                    else if (t < 0.9f)
                    {
                        aR = Quaternion.Euler(-160f, 0f, -20f);
                        breathe = Mathf.Sin(t * 30f) * 2f;                 // 施放微颤
                    }
                    else { _kind = AnimKind.Idle; }
                    break;
                }
                case AnimKind.Defend:
                {
                    _defendActive = Mathf.MoveTowards(_defendActive, 1f, dt * 6f);
                    body = Quaternion.Euler(8f, 0f, 0f);
                    aL = Quaternion.Euler(-150f * _defendActive, 0f, -20f * _defendActive); // 双臂交叉护前
                    aR = Quaternion.Euler(-150f * _defendActive, 0f, 20f * _defendActive);
                    break;
                }
                case AnimKind.HitReaction:
                {
                    float t = _animT;
                    if (t < 0.22f)
                    {
                        float k = t / 0.22f;
                        body = Quaternion.Euler(0f, 0f, 14f * k);
                        aR = Quaternion.Euler(10f * k, 0f, 6f);
                    }
                    else { _kind = AnimKind.Idle; }
                    break;
                }
                case AnimKind.Down:
                {
                    float k = Mathf.Clamp01(_animT / 0.5f);
                    _root.localRotation = Quaternion.Euler(0f, 0f, -90f * k); // 侧倒
                    _root.localPosition = new Vector3(0f, 0.5f * k, 0f);
                    return;
                }
                default: // Idle
                {
                    aL = Quaternion.Euler(IdleArmL.eulerAngles.x + breathe, 0f, IdleArmL.eulerAngles.z);
                    aR = Quaternion.Euler(IdleArmR.eulerAngles.x + breathe, 0f, IdleArmR.eulerAngles.z);
                    break;
                }
            }

            ApplyPose(body, aL, aR, lL, lR);
        }

        private void ApplyPose(Quaternion body, Quaternion aL, Quaternion aR, Quaternion lL, Quaternion lR)
        {
            _root.localRotation = Quaternion.Slerp(_root.localRotation, body, 10f * Time.deltaTime);
            _armL.localRotation = Quaternion.Slerp(_armL.localRotation, aL, 12f * Time.deltaTime);
            _armR.localRotation = Quaternion.Slerp(_armR.localRotation, aR, 12f * Time.deltaTime);
            _legL.localRotation = Quaternion.Slerp(_legL.localRotation, lL, 12f * Time.deltaTime);
            _legR.localRotation = Quaternion.Slerp(_legR.localRotation, lR, 12f * Time.deltaTime);
        }

        private static Transform MakePrimitive(PrimitiveType type, string name, Material mat, Vector3 scale)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            go.transform.localScale = scale;
            var col = go.GetComponent<Collider>();
            if (col != null) Object.Destroy(col);
            var r = go.GetComponent<Renderer>();
            if (r != null) r.sharedMaterial = mat;
            return go.transform;
        }

        private static Material MakeMat(Color c)
        {
            var shader = Shader.Find("Standard");
            var mat = new Material(shader != null ? shader : Shader.Find("Diffuse"));
            if (mat.HasProperty("_Color")) mat.color = c;
            return mat;
        }

        private static Color Lighten(Color c, float f)
        {
            return new Color(c.r + f, c.g + f, c.b + f, c.a);
        }
    }
}
