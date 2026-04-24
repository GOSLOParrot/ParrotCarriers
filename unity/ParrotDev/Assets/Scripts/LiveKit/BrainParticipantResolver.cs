using LiveKit;

/// <summary>
/// Finds the LiveKit Brain worker participant in a room. LiveKit Agents commonly use
/// identities prefixed with <c>agent-</c>; some deployments use plain <c>brain</c>.
/// Returns the <b>first</b> <c>agent-*</c> match, else first <c>brain</c> — same ambiguity as
/// Python <c>_find_unity_participant</c> when multiple agents exist; multi-agent rooms need a future explicit target.
/// </summary>
public static class BrainParticipantResolver
{
    public static string FindBrainParticipantId(Room room)
    {
        if (room?.RemoteParticipants == null || room.RemoteParticipants.Count == 0)
            return null;

        foreach (var p in room.RemoteParticipants.Values)
        {
            var id = p.Identity ?? "";
            if (id.Length > 0 && id.StartsWith("agent-", System.StringComparison.Ordinal))
                return id;
        }

        foreach (var p in room.RemoteParticipants.Values)
        {
            var id = p.Identity ?? "";
            if (string.Equals(id, "brain", System.StringComparison.OrdinalIgnoreCase))
                return id;
        }

        return null;
    }
}
