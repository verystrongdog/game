using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// Maps snake_case_lower JSON strings to PascalCase C# enum members and back.
/// Uses case-insensitive comparison on deserialization so values like "GABA"
/// in JSON match <c>Gaba</c> in the enum.
/// </summary>
public class SnakeCaseEnumConverter<T> : JsonConverter<T> where T : struct, Enum
{
    public override T Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        var str = reader.GetString()!;
        foreach (var value in Enum.GetValues<T>())
        {
            if (string.Equals(ToSnakeCase(value.ToString()), str, StringComparison.OrdinalIgnoreCase))
                return value;
        }
        throw new JsonException($"Unable to convert \"{str}\" to enum {typeof(T).Name}");
    }

    public override void Write(Utf8JsonWriter writer, T value, JsonSerializerOptions options)
    {
        writer.WriteStringValue(ToSnakeCase(value.ToString()));
    }

    private static string ToSnakeCase(string pascalCase)
    {
        var sb = new System.Text.StringBuilder();
        for (int i = 0; i < pascalCase.Length; i++)
        {
            char c = pascalCase[i];
            if (i > 0)
            {
                char prev = pascalCase[i - 1];
                // Underscore on: lowercase→uppercase, or letter→digit.
                // NOT on digit→letter — that keeps "5Ht" as "5ht" (single token).
                if ((char.IsUpper(c) && char.IsLower(prev)) ||
                    (char.IsDigit(c) && char.IsLetter(prev)))
                {
                    sb.Append('_');
                }
            }
            sb.Append(char.ToLowerInvariant(c));
        }
        return sb.ToString();
    }
}
