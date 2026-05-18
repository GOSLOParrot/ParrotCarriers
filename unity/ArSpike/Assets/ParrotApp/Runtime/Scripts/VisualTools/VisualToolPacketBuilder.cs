using System;
using System.Globalization;
using System.Text;
using UnityEngine;

namespace ParrotApp.VisualTools
{
    public static class VisualToolKinds
    {
        public const string BBox = "bbox";
        public const string Mag = "mag";
        public const string Focus = "focus";
    }

    public static class VisualToolPhases
    {
        public const string PreviewStart = "preview_start";
        public const string DragUpdate = "drag_update";
        public const string ResizeUpdate = "resize_update";
        public const string DwellTick = "dwell_tick";
        public const string Lock = "lock";
        public const string Unlock = "unlock";
        public const string Confirm = "confirm";
        public const string ExplicitSend = "explicit_send";
        public const string Cancel = "cancel";
        public const string Release = "release";
    }

    public static class VisualToolDeliveryPreferences
    {
        public const string Default = "default";
        public const string Silent = "silent";
        public const string IntentOnly = "intent_only";
        public const string C3 = "c3";
    }

    [Serializable]
    public struct VisualToolRegion
    {
        public float x;
        public float y;
        public float width;
        public float height;
        public string coordinate_space;

        public static VisualToolRegion ScreenNormalized(float x, float y, float width, float height)
        {
            return new VisualToolRegion
            {
                x = x,
                y = y,
                width = width,
                height = height,
                coordinate_space = "screen_normalized",
            }.Clamped();
        }

        public VisualToolRegion Clamped()
        {
            float w = Mathf.Clamp01(width);
            float h = Mathf.Clamp01(height);
            float left = Mathf.Clamp01(x);
            float top = Mathf.Clamp01(y);
            if (left + w > 1f) left = Mathf.Max(0f, 1f - w);
            if (top + h > 1f) top = Mathf.Max(0f, 1f - h);
            return new VisualToolRegion
            {
                x = left,
                y = top,
                width = w,
                height = h,
                coordinate_space = string.IsNullOrWhiteSpace(coordinate_space) ? "screen_normalized" : coordinate_space,
            };
        }
    }

    [Serializable]
    public struct VisualToolTimebase
    {
        public string clock_domain;
        public long wall_time_ms;
        public long monotonic_ms;
        public long media_time_us;
        public long sequence;
        public bool estimated;
        public string source_id;
    }

    [Serializable]
    public class VisualToolLifecyclePacket
    {
        public string tool_event_id = "";
        public string tool_id = "";
        public string tool_kind = "";
        public string interaction_phase = "";
        public VisualToolRegion region;
        public string pose_json = "{}";
        public string source_surface = "formal_home.tool_overlay";
        public VisualToolTimebase timebase;
        public string asset_ref = "";
        public string asset_path = "";
        public string asset_uri = "";
        public string mime_type = "";
        public string evidence_id = "";
        public float attention_hint = 0f;
        public string delivery_preference = VisualToolDeliveryPreferences.Default;
        public string subject_hint = "";
        public string label = "";
        public string meta_json = "{}";
    }

    public static class VisualToolPacketBuilder
    {
        public static VisualToolLifecyclePacket CreateLifecycle(
            string toolId,
            string toolKind,
            string phase,
            VisualToolRegion region,
            string sourceSurface,
            string deliveryPreference = VisualToolDeliveryPreferences.Default)
        {
            return new VisualToolLifecyclePacket
            {
                tool_event_id = GenerateEventId(),
                tool_id = string.IsNullOrWhiteSpace(toolId) ? GenerateToolId(toolKind) : toolId,
                tool_kind = toolKind ?? "",
                interaction_phase = phase ?? "",
                region = region.Clamped(),
                source_surface = string.IsNullOrWhiteSpace(sourceSurface) ? "formal_home.tool_overlay" : sourceSurface,
                timebase = UnityTimebase(),
                delivery_preference = string.IsNullOrWhiteSpace(deliveryPreference)
                    ? VisualToolDeliveryPreferences.Default
                    : deliveryPreference,
            };
        }

        public static VisualToolTimebase UnityTimebase(string sourceId = "unity:formal_app")
        {
            return new VisualToolTimebase
            {
                clock_domain = "unity",
                wall_time_ms = UnixMilliseconds(),
                monotonic_ms = (long)Math.Round(Time.realtimeSinceStartupAsDouble * 1000.0),
                media_time_us = 0,
                sequence = 0,
                estimated = false,
                source_id = sourceId,
            };
        }

        public static string ToJson(VisualToolLifecyclePacket packet)
        {
            if (packet == null) packet = new VisualToolLifecyclePacket();
            var ci = CultureInfo.InvariantCulture;
            var sb = new StringBuilder(512);
            sb.Append('{');
            AppendString(sb, "tool_event_id", packet.tool_event_id, ref ci, trailingComma: true);
            AppendString(sb, "tool_id", packet.tool_id, ref ci, trailingComma: true);
            AppendString(sb, "tool_kind", packet.tool_kind, ref ci, trailingComma: true);
            AppendString(sb, "interaction_phase", packet.interaction_phase, ref ci, trailingComma: true);
            sb.Append("\"region\":").Append(RegionJson(packet.region)).Append(',');
            sb.Append("\"pose\":").Append(ObjectJson(packet.pose_json)).Append(',');
            AppendString(sb, "source_surface", packet.source_surface, ref ci, trailingComma: true);
            sb.Append("\"timebase\":").Append(TimebaseJson(packet.timebase)).Append(',');
            AppendString(sb, "asset_ref", packet.asset_ref, ref ci, trailingComma: true);
            AppendString(sb, "asset_path", packet.asset_path, ref ci, trailingComma: true);
            AppendString(sb, "asset_uri", packet.asset_uri, ref ci, trailingComma: true);
            AppendString(sb, "mime_type", packet.mime_type, ref ci, trailingComma: true);
            AppendString(sb, "evidence_id", packet.evidence_id, ref ci, trailingComma: true);
            sb.Append("\"attention_hint\":").Append(packet.attention_hint.ToString("R", ci)).Append(',');
            AppendString(sb, "delivery_preference", packet.delivery_preference, ref ci, trailingComma: true);
            AppendString(sb, "subject_hint", packet.subject_hint, ref ci, trailingComma: true);
            AppendString(sb, "label", packet.label, ref ci, trailingComma: true);
            sb.Append("\"meta\":").Append(ObjectJson(packet.meta_json));
            sb.Append('}');
            return sb.ToString();
        }

        public static string RegionJson(VisualToolRegion region)
        {
            var ci = CultureInfo.InvariantCulture;
            var r = region.Clamped();
            return "{"
                   + "\"x\":" + r.x.ToString("R", ci) + ","
                   + "\"y\":" + r.y.ToString("R", ci) + ","
                   + "\"width\":" + r.width.ToString("R", ci) + ","
                   + "\"height\":" + r.height.ToString("R", ci) + ","
                   + "\"coordinate_space\":" + QuoteJson(string.IsNullOrWhiteSpace(r.coordinate_space) ? "screen_normalized" : r.coordinate_space)
                   + "}";
        }

        public static string TimebaseJson(VisualToolTimebase timebase)
        {
            var ci = CultureInfo.InvariantCulture;
            string clockDomain = string.IsNullOrWhiteSpace(timebase.clock_domain) ? "unity" : timebase.clock_domain;
            string sourceId = string.IsNullOrWhiteSpace(timebase.source_id) ? "unity:formal_app" : timebase.source_id;
            return "{"
                   + "\"clock_domain\":" + QuoteJson(clockDomain) + ","
                   + "\"wall_time_ms\":" + timebase.wall_time_ms.ToString(ci) + ","
                   + "\"monotonic_ms\":" + timebase.monotonic_ms.ToString(ci) + ","
                   + "\"media_time_us\":" + timebase.media_time_us.ToString(ci) + ","
                   + "\"sequence\":" + timebase.sequence.ToString(ci) + ","
                   + "\"estimated\":" + (timebase.estimated ? "true" : "false") + ","
                   + "\"source_id\":" + QuoteJson(sourceId)
                   + "}";
        }

        public static string GenerateToolId(string toolKind)
        {
            string prefix = "vt";
            if (string.Equals(toolKind, VisualToolKinds.BBox, StringComparison.OrdinalIgnoreCase))
                prefix = "bb";
            else if (string.Equals(toolKind, VisualToolKinds.Mag, StringComparison.OrdinalIgnoreCase))
                prefix = "mag";
            else if (string.Equals(toolKind, VisualToolKinds.Focus, StringComparison.OrdinalIgnoreCase))
                prefix = "fc";
            return prefix + "_" + Guid.NewGuid().ToString("N").Substring(0, 8);
        }

        public static string GenerateEventId()
        {
            return "vtool_" + UnixMilliseconds().ToString("x12") + "_" + Guid.NewGuid().ToString("N").Substring(0, 8);
        }

        public static long UnixMilliseconds()
        {
            return (long)((DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalMilliseconds);
        }

        public static string QuoteJson(string value)
        {
            if (value == null) return "\"\"";
            var sb = new StringBuilder(value.Length + 2);
            sb.Append('"');
            foreach (char c in value)
            {
                switch (c)
                {
                    case '\\': sb.Append("\\\\"); break;
                    case '"': sb.Append("\\\""); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.AppendFormat("\\u{0:x4}", (int)c);
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
            return sb.ToString();
        }

        private static void AppendString(
            StringBuilder sb,
            string key,
            string value,
            ref CultureInfo ci,
            bool trailingComma)
        {
            sb.Append('"').Append(key).Append("\":").Append(QuoteJson(value ?? ""));
            if (trailingComma) sb.Append(',');
        }

        private static string ObjectJson(string value)
        {
            if (string.IsNullOrWhiteSpace(value)) return "{}";
            string trimmed = value.Trim();
            if (trimmed.StartsWith("{", StringComparison.Ordinal) && trimmed.EndsWith("}", StringComparison.Ordinal))
                return trimmed;
            return "{}";
        }
    }
}
