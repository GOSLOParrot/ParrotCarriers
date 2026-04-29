using System;
using UnityEngine;

/// <summary>
/// Minimal Sprint4 ECP DTOs shared by Unity RPC handlers.
///
/// These classes intentionally stay JsonUtility-friendly: public fields only,
/// no dictionaries, and no dependency on a third-party JSON package. Legacy RPC
/// handlers read the optional "_ecp" payload field and return an ECP-shaped
/// ack.
///
/// DRIFT NOTE (Sprint4 ECP-minimal, 2026-04-29):
///   `expires_at` is intentionally `double` here even though the Python
///   `EcpCommand` model stores it as `float`. JsonUtility round-trips it as
///   a float on the wire either way, but Unix-epoch timestamps lose useful
///   precision when squeezed into a 32-bit float (~24h granularity around
///   2026 epoch). Keeping the in-memory representation as `double` lets the
///   `expires_at` check actually mean something.
/// </summary>
[Serializable]
public class EcpCommandDto
{
    public string schema_version = "ecp.v2.alpha";
    public string command_id = "";
    public string kind = "";
    public double issued_at;
    public double valid_after;
    public double expires_at;
    public string layer = "intent";
    public int priority = 50;
    public string interruptibility = "interruptible";

    /// <summary>
    /// Returns true when the command has an `expires_at` and Unix-time now is
    /// past it. A zero/negative `expires_at` means "no expiry" by convention,
    /// matching `EcpCommand.for_legacy_rpc(expires_in_s=0)` on the Python side.
    /// </summary>
    public bool IsExpired(double nowUnix)
    {
        return expires_at > 0.0 && nowUnix > expires_at;
    }
}

[Serializable]
public class EcpFrontendStateDto
{
    public string body_state = "";
    public string head_state = "";
    public string cognitive_state = "";
    public string[] active_locks = new string[0];
    public string active_command_id = "";
    public string video_tier = "";
    public string app_lifecycle_state = "";
    public string ar_tracking_state = "";

    public static EcpFrontendStateDto ForBody(string bodyState, string commandId = "", string[] locks = null)
    {
        return new EcpFrontendStateDto
        {
            body_state = bodyState ?? "",
            active_command_id = commandId ?? "",
            active_locks = locks ?? new string[0],
        };
    }

    public static EcpFrontendStateDto ForVideoTier(string tier, string commandId = "")
    {
        return new EcpFrontendStateDto
        {
            video_tier = tier ?? "",
            active_command_id = commandId ?? "",
            // Video tier changes belong to the vision channel, not the body
            // resource; do not falsely report a body lock here.
            active_locks = new string[0],
        };
    }
}

[Serializable]
public class EcpAckDto
{
    public string schema_version = "ecp.v2.alpha";
    public string command_id = "";
    public string ack_id = "";
    public string status = "";
    public string reason = "";
    public EcpFrontendStateDto frontend_state = new EcpFrontendStateDto();
    public double received_at;
    public double started_at;
    public double completed_at;
    public string detail = "";
}

/// <summary>
/// Builders for ECP ack JSON. The `reason` argument follows the small
/// vocabulary defined in `sprint4_protocol_v2_ecp.md` §5.2:
///   applied / unchanged / no_unity / no_video_publisher / permission_denied /
///   expired / micro_lock / illegal_transition / incompatible_state /
///   transport / malformed / timeout / unknown_tier
/// Do NOT pass action names like "flyTo" / "animate" as reasons — those are
/// already recoverable from `EcpCommand.kind` via `command_id`.
/// </summary>
public static class EcpAckJson
{
    public const string ReasonApplied = "applied";
    public const string ReasonUnchanged = "unchanged";
    public const string ReasonExpired = "expired";
    public const string ReasonRejected = "rejected";
    public const string ReasonFailed = "failed";
    public const string ReasonMalformed = "malformed";
    public const string ReasonTransport = "transport";
    public const string ReasonNoVideoPublisher = "no_video_publisher";
    public const string ReasonUnknownTier = "unknown_tier";

    public static string Completed(EcpCommandDto command, EcpFrontendStateDto state = null, string reason = ReasonApplied)
    {
        double now = UnixSeconds();
        string commandId = CommandId(command);
        var ack = new EcpAckDto
        {
            command_id = commandId,
            ack_id = NewAckId(),
            status = "completed",
            reason = string.IsNullOrEmpty(reason) ? ReasonApplied : reason,
            frontend_state = state ?? new EcpFrontendStateDto(),
            received_at = now,
            started_at = now,
            completed_at = now,
            detail = "",
        };
        if (ack.frontend_state != null && string.IsNullOrEmpty(ack.frontend_state.active_command_id))
            ack.frontend_state.active_command_id = commandId;
        return JsonUtility.ToJson(ack);
    }

    public static string Rejected(EcpCommandDto command, string reason, string detail = "")
    {
        double now = UnixSeconds();
        var ack = new EcpAckDto
        {
            command_id = CommandId(command),
            ack_id = NewAckId(),
            status = "rejected",
            reason = string.IsNullOrEmpty(reason) ? ReasonRejected : reason,
            frontend_state = new EcpFrontendStateDto(),
            received_at = now,
            started_at = 0.0,
            completed_at = now,
            detail = detail ?? "",
        };
        return JsonUtility.ToJson(ack);
    }

    public static string Expired(EcpCommandDto command, string detail = "")
    {
        double now = UnixSeconds();
        var ack = new EcpAckDto
        {
            command_id = CommandId(command),
            ack_id = NewAckId(),
            status = "expired",
            reason = ReasonExpired,
            frontend_state = new EcpFrontendStateDto(),
            received_at = now,
            started_at = 0.0,
            completed_at = now,
            detail = detail ?? "",
        };
        return JsonUtility.ToJson(ack);
    }

    public static string Failed(EcpCommandDto command, string detail, string reason = ReasonFailed)
    {
        double now = UnixSeconds();
        var ack = new EcpAckDto
        {
            command_id = CommandId(command),
            ack_id = NewAckId(),
            status = "failed",
            reason = string.IsNullOrEmpty(reason) ? ReasonFailed : reason,
            frontend_state = new EcpFrontendStateDto(),
            received_at = now,
            started_at = 0.0,
            completed_at = now,
            detail = detail ?? "",
        };
        return JsonUtility.ToJson(ack);
    }

    /// <summary>Unix-epoch seconds with sub-second precision (double).</summary>
    public static double UnixSeconds()
    {
        return (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;
    }

    private static string CommandId(EcpCommandDto command)
    {
        return command != null ? (command.command_id ?? "") : "";
    }

    private static string NewAckId()
    {
        return "ack_" + Guid.NewGuid().ToString("N").Substring(0, 12);
    }
}
