using System;
using LiveKit;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Finds the LiveKit Brain worker participant in a room.
    /// LiveKit Agents commonly use identities prefixed with <c>agent-</c>;
    /// some deployments use plain <c>brain</c>.
    /// Returns the <b>first</b> <c>agent-*</c> match, else first <c>brain</c>.
    ///
    /// 与 Python 端 <c>_rpc_bridge._find_unity_participant</c> 对偶。
    /// 多 agent 房间需要显式 target，留 P2+ 处理。
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
                if (id.Length > 0 && id.StartsWith("agent-", StringComparison.Ordinal))
                    return id;
            }

            foreach (var p in room.RemoteParticipants.Values)
            {
                var id = p.Identity ?? "";
                if (string.Equals(id, "brain", StringComparison.OrdinalIgnoreCase))
                    return id;
            }

            return null;
        }
    }
}
