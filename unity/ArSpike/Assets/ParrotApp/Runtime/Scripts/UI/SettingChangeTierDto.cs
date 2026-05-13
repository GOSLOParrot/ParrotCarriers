using System;
using UnityEngine;

namespace ParrotApp.UI
{
    /// <summary>
    /// Mirror of <c>data/registries/setting_change_tier.json</c> shape so the
    /// Unity startup page and menu corner can render the right toast / confirm
    /// dialog without hard-coding "this knob is cold-start only".
    ///
    /// Source: Phase 4.1 of the ECS Orchestrator audit
    /// (<c>app_v1_brain_cold_start_line_lifecycle_audit_20260511.md</c>).
    ///
    /// Tier semantics:
    ///   0  BB-write only (instant, no UI prompt)
    ///   1  LiveKit reconnect (Brain process stays up)
    ///   2  Brain process restart (5–10s downtime, progress bar)
    ///   3  Operator-only (never offered to Unity UI)
    ///
    /// Wire: this DTO is filled either from the Brain RPC
    /// <c>getRoomSettingSnapshot</c> response (per-row <c>tier</c> field on
    /// each line selector and the top-level <c>compatibility.tier</c>) or by
    /// fetching <c>setting_change_tier.json</c> directly when the orchestrator
    /// isn't reachable.
    /// </summary>
    [Serializable]
    public class SettingChangeTierDto
    {
        public int tier;
        public string label = string.Empty;
        public string summary = string.Empty;
        public string summary_zh = string.Empty;
        public string ui_action = string.Empty;

        public bool RequiresConfirm =>
            tier >= 1 && (ui_action ?? string.Empty).StartsWith("confirm");

        public bool IsOperatorOnly => tier >= 3;

        public bool IsSilent => tier == 0;
    }

    public static class SettingChangeTierUiHelper
    {
        /// <summary>
        /// Pick the toast / dialog shape the startup page or menu corner
        /// should render for a tier transition.
        /// </summary>
        public static SettingChangeTierUiAction Decide(SettingChangeTierDto dto, string lang)
        {
            if (dto == null)
            {
                return new SettingChangeTierUiAction
                {
                    kind = SettingChangeTierUiActionKind.SilentApply,
                };
            }

            if (dto.IsOperatorOnly)
            {
                return new SettingChangeTierUiAction
                {
                    kind = SettingChangeTierUiActionKind.Block,
                    title = "Operator only",
                    body = LocalizedSummary(dto, lang),
                };
            }

            switch (dto.tier)
            {
                case 0:
                    return new SettingChangeTierUiAction
                    {
                        kind = SettingChangeTierUiActionKind.SilentApply,
                    };
                case 1:
                    return new SettingChangeTierUiAction
                    {
                        kind = SettingChangeTierUiActionKind.ConfirmReconnect,
                        title = string.IsNullOrEmpty(dto.label) ? "LiveKit reconnect" : dto.label,
                        body = LocalizedSummary(dto, lang),
                    };
                case 2:
                    return new SettingChangeTierUiAction
                    {
                        kind = SettingChangeTierUiActionKind.ConfirmProcessRestart,
                        title = string.IsNullOrEmpty(dto.label) ? "Brain process restart" : dto.label,
                        body = LocalizedSummary(dto, lang),
                    };
                default:
                    return new SettingChangeTierUiAction
                    {
                        kind = SettingChangeTierUiActionKind.SilentApply,
                    };
            }
        }

        private static string LocalizedSummary(SettingChangeTierDto dto, string lang)
        {
            if (lang == "zh" && !string.IsNullOrEmpty(dto.summary_zh))
            {
                return dto.summary_zh;
            }
            return dto.summary ?? string.Empty;
        }
    }

    public enum SettingChangeTierUiActionKind
    {
        SilentApply,
        ConfirmReconnect,
        ConfirmProcessRestart,
        Block,
    }

    public struct SettingChangeTierUiAction
    {
        public SettingChangeTierUiActionKind kind;
        public string title;
        public string body;
    }
}
