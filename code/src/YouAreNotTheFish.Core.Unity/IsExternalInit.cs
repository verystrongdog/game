// netstandard2.1 的 polyfill（#155 · Q6b 裁定 A）
//
// C# 9 的 `init` 取值器与 `record` 需要 `System.Runtime.CompilerServices.IsExternalInit` 这个
// **标记类型**存在；netstandard2.1 不含它（.NET 5+ 才有）。声明一个空类型即可，编译器据此
// 生成 init 访问器，运行时不参与任何逻辑——这是业界标准做法，不是本仓的发明。
//
// 为什么需要：桥接工程链接的 Types/CalibrationConfig.cs 是 `sealed record` + `init` 属性。
namespace System.Runtime.CompilerServices
{
    internal static class IsExternalInit { }
}
