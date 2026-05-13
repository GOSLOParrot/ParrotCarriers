const dictionaries = {
  en: {
    "nav.opsHealth": "Ops Health",
    "nav.runtimeMonitor": "Runtime Monitor",
    "nav.linebVoice": "LineB Voice",
    "nav.menuCanvas": "Menu Canvas",
    "nav.memoryGraph": "Memory Graph",
    "nav.graphiti": "Graphiti",
    "ops.title": "Ops Health",
    "runtime.title": "Runtime Monitor",
    "lineb.title": "LineB Voice",
    "canvas.title": "Menu Canvas",
    "memory.title": "Memory Graph",
    "overview.label": "System State",
    "actions.refresh": "Refresh",
    "actions.loading": "Loading",
    "actions.pause": "Pause",
    "actions.resume": "Resume",
    "metrics.modules": "Modules",
    "metrics.warnings": "Warnings",
    "metrics.selection": "Selection",
    "topology.title": "Status Topology",
    "topology.console": "Web Console",
    "topology.orchestrator": "Orchestrator",
    "topology.status": "Status Snapshot",
    "topology.modules": "Module Heartbeats",
    "panes.moduleHealth": "Module Health",
    "panes.moduleTable": "Module Table",
    "panes.runtimeConfig": "Runtime Config",
    "panes.brainSnapshot": "Brain Snapshot",
    "panes.containers": "Containers",
    "panes.warnings": "Warnings",
    "table.module": "Module",
    "table.state": "State",
    "table.type": "Type",
    "table.layers": "Layers",
    "table.stale": "Stale",
    "table.note": "Note",
    "pills.read": "read",
    "pills.empty": "empty",
    "pills.online": "online",
    "pills.degraded": "degraded",
    "pills.checking": "checking",
    "pills.test": "test",
    "settings.title": "Settings",
    "settings.language": "Language",
    "settings.languageHint": "Applies to this browser.",
    "states.connected": "connected",
    "states.degraded": "degraded",
    "states.offline": "offline",
    "states.unauthorized": "unauthorized",
    "states.error": "error",
    "states.aligned": "aligned",
    "states.drift": "drift",
    "states.online": "online",
    "states.offlineShort": "offline",
    "empty.noData": "No data",
    "empty.noModuleHeartbeat": "No module heartbeat data.",
    "empty.noContainer": "No container data.",
    "empty.noWarnings": "No warnings.",
    "empty.never": "never",
    "last.waiting": "Waiting for status...",
    "last.fetched": "Last fetch {time} in {ms} ms",
    "errors.loadFailed": "Load failed: {message}",
    "auth.mode": "auth: {mode}",
    "auth.orchestrator": "orchestrator: {url}",
    "auth.secretMissing": "Orchestrator requires Bearer auth; set PARROT_ORCH_SECRET for the Web Console process.",
    "topology.healthOk": "/health ok",
    "topology.healthMissing": "/health unreachable",
    "topology.statusOk": "/status ok",
    "topology.statusDenied": "/status needs Bearer",
    "topology.statusMissing": "/status unavailable",
    "topology.moduleCount": "{count} online",
    "module.placeholder": "waiting for heartbeat",
    "lineb.route": "Voice Route",
    "lineb.setNoVideo": "Set No-Video Route",
    "lineb.micCheck": "Mic Permission",
    "lineb.profile": "Line Profile",
    "lineb.applyProfile": "Apply",
    "lineb.tts": "TTS Segment",
    "lineb.registerTts": "Register",
    "lineb.micInput": "Mic Input",
    "lineb.echoScore": "Echo score",
    "lineb.submitMic": "Submit",
    "lineb.result": "Result",
    "lineb.micReady": "microphone available",
    "lineb.micBlocked": "microphone blocked",
    "lineb.routeReady": "no-video route applied",
    "lineb.noProfiles": "No profiles",
    "livekit.room": "LiveKit Room",
    "livekit.roomId": "Room",
    "livekit.identity": "Identity",
    "livekit.mint": "Mint Web Token",
    "livekit.connectAudio": "Connect Audio",
    "livekit.disconnect": "Disconnect",
    "livekit.ready": "token minted; ready for browser audio client",
    "livekit.unavailable": "token mint unavailable",
    "livekit.connecting": "connecting to LiveKit...",
    "livekit.connected": "audio connected",
    "livekit.disconnected": "audio disconnected",
    "livekit.remoteAudio": "remote audio attached",
    "livekit.needsToken": "minting Web Token first...",
    "livekit.importFailed": "LiveKit browser client failed to load",
    "livekit.events": "Connection Events",
    "livekit.transcripts": "Transcripts",
    "livekit.noEvents": "No LiveKit events yet.",
    "livekit.noTranscripts": "No transcripts in this browser session yet.",
    "livekit.reconnecting": "reconnecting...",
    "livekit.signalReconnecting": "signal reconnecting...",
    "livekit.reconnected": "audio reconnected",
    "livekit.signalConnected": "signal connected",
    "livekit.stateChanged": "state changed",
    "livekit.manualDisconnect": "manual disconnect",
    "livekit.trackSubscribed": "remote track subscribed",
    "livekit.trackUnsubscribed": "remote track unsubscribed",
    "livekit.transcriptReceived": "transcript received",
    "livekit.final": "final",
    "livekit.partial": "partial",
    "livekit.error": "LiveKit error",
    "livekit.tokenMinted": "token minted",
    "canvas.label": "Canvas State",
    "canvas.modules": "Modules",
    "canvas.refs": "Refs",
    "canvas.tools": "Tools",
    "canvas.workspaces": "Workspaces",
    "canvas.map": "Canvas Map",
    "canvas.activeWorkspace": "active workspace",
    "memory.label": "Graph Snapshot",
    "memory.blackboard": "Blackboard",
    "memory.intent": "Intent Workspace",
    "memory.refs": "Refs",
    "memory.l2b": "L2-B",
    "memory.lanes": "Memory Lanes",
    "memory.visualWorkspace": "Visual Workspace",
    "memory.opsCockpit": "Memory Operations Cockpit",
    "memory.liveHint": "Active Memory view polls every 5 seconds; Pause freezes the surface.",
    "memory.sourceBuckets": "Source Buckets",
    "memory.dsgState": "DSG State",
    "memory.buckets": "buckets",
    "memory.open": "open",
    "memory.waitingForNodes": "waiting for L2-B nodes",
    "memory.selectedActions": "Selected Node Actions",
    "memory.directHint": "Click a L2-B node, then draft a safe operation.",
    "memory.useSelected": "Use Selected",
    "memory.setEdgeFrom": "Edge From",
    "memory.setEdgeTo": "Edge To",
    "memory.edgeDirectHint": "Use two selected L2-B nodes or paste UUIDs.",
    "memory.receipts": "Receipts",
    "memory.clearPreview": "Clear Preview",
    "memory.preview": "preview",
    "memory.advancedDrafts": "Advanced Drafts",
    "memory.operatorSafe": "operator-safe",
    "memory.obsidianSettingNode": "Obsidian Setting Node",
    "memory.advancedNotes": "Notes",
    "memory.advancedHint": "Raw JSON and true writes stay behind explicit operator paths; the main cockpit keeps safe dry-run actions visible.",
    "memory.graphMap": "L2-B Map",
    "memory.toolArtifacts": "Tool Artifacts",
    "memory.nodes": "nodes",
    "memory.edges": "edges",
    "memory.present": "{count} present",
    "memory.declared": "{count} declared",
    "memory.readOnly": "read-only snapshot",
    "memory.noNodes": "waiting for L2-B nodes",
    "memory.noArtifacts": "no active artifacts",
    "memory.blackboardKeys": "Blackboard Keys",
    "memory.blackboardActivity": "Blackboard Activity",
    "memory.intentRefs": "Intent Refs",
    "memory.detail": "Memory Detail",
    "memory.sequence": "seq {count}",
    "memory.emptyKeys": "no present keys",
    "memory.emptyRefs": "no staged refs",
    "memory.topAttention": "Top Attention",
    "memory.scope": "scope",
    "memory.writer": "writer",
    "memory.expires": "expires",
    "memory.owner": "owner",
    "memory.linked": "linked",
    "memory.liveSnapshot": "live snapshot",
    "memory.noSelection": "select a node, key, or ref",
    "memory.graphPlaceholder": "live graph will appear when L2-B has nodes",
    "memory.edgeCount": "{count} edges",
    "memory.attention": "attention",
    "memory.kind": "kind",
    "memory.source": "source",
    "memory.confirmation": "confirmation",
    "memory.connections": "connections",
    "memory.generated": "generated {time}",
    "memory.operatorWorkbench": "Operator Workbench",
    "memory.l15Pool": "L1.5 Pool",
    "memory.operation": "Operation",
    "memory.payload": "Payload JSON",
    "memory.draftBucketOp": "Draft Bucket Op",
    "memory.bucketDryRun": "Bucket Dry-Run",
    "memory.bucketQuickHint": "Quick bucket drafts",
    "memory.freeze": "Freeze",
    "memory.unfreeze": "Unfreeze",
    "memory.clear": "Clear",
    "memory.pressure": "pressure",
    "memory.profile": "Profile",
    "memory.labelField": "Label",
    "memory.draft": "Draft",
    "memory.dryRun": "Dry Run",
    "memory.l2bCrud": "L2-B Node CRUD",
    "memory.draftNode": "Draft Node",
    "memory.createDryRun": "Create Dry-Run",
    "memory.targetUuid": "Target UUID",
    "memory.updateDryRun": "Update Dry-Run",
    "memory.deleteUuid": "Delete UUID",
    "memory.deleteDryRun": "Delete Dry-Run",
    "memory.edgeDraft": "Edge Draft",
    "memory.draftEdge": "Draft Edge",
    "memory.edgeDryRun": "Edge Dry-Run",
    "memory.allKinds": "All kinds",
    "memory.applyFilters": "Apply",
    "memory.bucket": "bucket",
    "memory.changed": "changed",
    "memory.noActivity": "no activity yet",
    "memory.visible": "visible",
    "memory.hidden": "{count} hidden",
    "memory.crossCompartment": "cross",
    "memory.graphModeAll": "All graph",
    "memory.graphModeSelected": "Selected neighborhood",
    "memory.graphModeAttention": "Top attention",
    "memory.canvasOps": "Canvas Ops",
    "memory.createPreview": "Create Preview",
    "memory.grouped": "grouped",
    "memory.eventDriven": "event",
    "memory.refLinks": "ref links",
    "runtime.label": "Runtime",
    "runtime.scheduler": "Scheduler",
    "runtime.nanobot": "Nanobot",
    "runtime.plans": "Plans",
    "runtime.agentTeam": "Agent Team",
    "runtime.blackboard": "Blackboard",
    "runtime.collaboration": "Collaboration",
    "runtime.activeTasks": "Active Tasks",
    "runtime.reports": "Reports",
    "runtime.channels": "Channels",
    "runtime.routeOrder": "Route Order",
    "runtime.taskTypes": "Task Types",
    "runtime.currentPlan": "Current Plan",
    "runtime.noTasks": "no active tasks",
    "runtime.noPlans": "no plans",
    "runtime.readOnly": "read-only runtime snapshot",
    "runtime.placeholder": "V1 placeholder",
    "runtime.triggerLab": "Trigger Lab",
    "runtime.triggerPalette": "Trigger Palette",
    "runtime.triggerPaletteHint": "Preset buttons live above; raw JSON stays here for custom dry-run events.",
    "runtime.rawEvent": "raw event",
    "runtime.draftEvent": "Draft Event",
    "runtime.fireDryRun": "Fire Dry-Run",
    "runtime.messageCheck": "Message Check",
    "runtime.messagePush": "Message Push Test",
    "runtime.llmPush": "LLM Context Push",
    "runtime.schedulerTick": "Scheduler Tick",
    "runtime.calendarTest": "Calendar Test",
    "runtime.customEvent": "Custom Event Draft",
    "runtime.planGraph": "Plan Graph",
    "runtime.channelFlow": "Channel Flow",
    "runtime.safeSurface": "safe surface",
    "runtime.deps": "deps",
    "runtime.result": "result",
    "runtime.critical": "critical",
    "runtime.ready": "ready",
    "runtime.blocked": "blocked",
    "runtime.stepDetail": "Step Detail",
    "runtime.expectedTool": "tool",
    "runtime.nanobotTask": "nanobot",
    "runtime.started": "started",
    "runtime.completed": "completed",
    "runtime.error": "error",
    "graphiti.title": "Graphiti",
    "graphiti.label": "Memory Core",
    "graphiti.status": "Status",
    "graphiti.partitions": "Partitions",
    "graphiti.search": "Search",
    "graphiti.query": "Query",
    "graphiti.partition": "Partition",
    "graphiti.limit": "Limit",
    "graphiti.runSearch": "Search",
    "graphiti.results": "Results",
    "graphiti.episodeDraft": "Episode Draft",
    "graphiti.episodeName": "Name",
    "graphiti.episodeBody": "Body",
    "graphiti.draft": "Draft",
    "graphiti.dryRun": "Dry Run",
    "graphiti.available": "available",
    "graphiti.unavailable": "optional extra missing",
    "graphiti.noPartitions": "no partitions",
    "graphiti.noResults": "no results yet",
    "graphiti.operatorNote": "Writes stay dry-run until operator mode is explicitly enabled.",
  },
  zh: {
    "nav.opsHealth": "\u8fd0\u884c\u5065\u5eb7",
    "nav.runtimeMonitor": "\u8fd0\u884c\u76d1\u63a7",
    "nav.linebVoice": "LineB \u8bed\u97f3",
    "nav.menuCanvas": "\u83dc\u5355\u753b\u5e03",
    "nav.memoryGraph": "\u8bb0\u5fc6\u56fe\u8c31",
    "nav.graphiti": "Graphiti",
    "ops.title": "\u8fd0\u884c\u5065\u5eb7",
    "runtime.title": "\u8fd0\u884c\u76d1\u63a7",
    "lineb.title": "LineB \u8bed\u97f3",
    "canvas.title": "\u83dc\u5355\u753b\u5e03",
    "memory.title": "\u8bb0\u5fc6\u56fe\u8c31",
    "overview.label": "\u7cfb\u7edf\u72b6\u6001",
    "actions.refresh": "\u5237\u65b0",
    "actions.loading": "\u52a0\u8f7d\u4e2d",
    "actions.pause": "\u6682\u505c",
    "actions.resume": "\u7ee7\u7eed",
    "metrics.modules": "\u6a21\u5757",
    "metrics.warnings": "\u8b66\u544a",
    "metrics.selection": "\u9009\u62e9",
    "topology.title": "\u72b6\u6001\u62d3\u6251",
    "topology.console": "Web \u63a7\u5236\u53f0",
    "topology.orchestrator": "\u7f16\u6392\u5668",
    "topology.status": "\u72b6\u6001\u5feb\u7167",
    "topology.modules": "\u6a21\u5757\u5fc3\u8df3",
    "panes.moduleHealth": "\u6a21\u5757\u5065\u5eb7",
    "panes.moduleTable": "\u6a21\u5757\u8868",
    "panes.runtimeConfig": "\u8fd0\u884c\u914d\u7f6e",
    "panes.brainSnapshot": "Brain \u5feb\u7167",
    "panes.containers": "\u5bb9\u5668",
    "panes.warnings": "\u8b66\u544a",
    "table.module": "\u6a21\u5757",
    "table.state": "\u72b6\u6001",
    "table.type": "\u7c7b\u578b",
    "table.layers": "\u5c42\u7ea7",
    "table.stale": "\u5ef6\u8fdf",
    "table.note": "\u5907\u6ce8",
    "pills.read": "\u53ea\u8bfb",
    "pills.empty": "\u7a7a",
    "pills.online": "\u5728\u7ebf",
    "pills.degraded": "\u964d\u7ea7",
    "pills.checking": "\u68c0\u67e5\u4e2d",
    "pills.test": "\u6d4b\u8bd5",
    "settings.title": "\u8bbe\u7f6e",
    "settings.language": "\u8bed\u8a00",
    "settings.languageHint": "\u4ec5\u5f71\u54cd\u5f53\u524d\u6d4f\u89c8\u5668\u3002",
    "states.connected": "\u5df2\u8fde\u63a5",
    "states.degraded": "\u964d\u7ea7",
    "states.offline": "\u79bb\u7ebf",
    "states.unauthorized": "\u672a\u6388\u6743",
    "states.error": "\u9519\u8bef",
    "states.aligned": "\u4e00\u81f4",
    "states.drift": "\u6f02\u79fb",
    "states.online": "\u5728\u7ebf",
    "states.offlineShort": "\u79bb\u7ebf",
    "empty.noData": "\u6682\u65e0\u6570\u636e",
    "empty.noModuleHeartbeat": "\u6682\u65e0\u6a21\u5757\u5fc3\u8df3\u6570\u636e\u3002",
    "empty.noContainer": "\u6682\u65e0\u5bb9\u5668\u6570\u636e\u3002",
    "empty.noWarnings": "\u6ca1\u6709\u8b66\u544a\u3002",
    "empty.never": "\u4ece\u672a",
    "last.waiting": "\u7b49\u5f85\u72b6\u6001\u6570\u636e...",
    "last.fetched": "\u4e0a\u6b21\u5237\u65b0 {time}\uff0c\u8017\u65f6 {ms} ms",
    "errors.loadFailed": "\u52a0\u8f7d\u5931\u8d25\uff1a{message}",
    "auth.mode": "\u8ba4\u8bc1\uff1a{mode}",
    "auth.orchestrator": "\u7f16\u6392\u5668\uff1a{url}",
    "auth.secretMissing": "\u7f16\u6392\u5668\u9700\u8981 Bearer \u8ba4\u8bc1\uff1b\u8bf7\u4e3a Web Console \u8fdb\u7a0b\u8bbe\u7f6e PARROT_ORCH_SECRET\u3002",
    "topology.healthOk": "/health \u6b63\u5e38",
    "topology.healthMissing": "/health \u4e0d\u53ef\u8fbe",
    "topology.statusOk": "/status \u6b63\u5e38",
    "topology.statusDenied": "/status \u9700\u8981 Bearer",
    "topology.statusMissing": "/status \u4e0d\u53ef\u7528",
    "topology.moduleCount": "{count} \u4e2a\u5728\u7ebf",
    "module.placeholder": "\u7b49\u5f85\u5fc3\u8df3",
    "lineb.route": "\u8bed\u97f3\u8def\u7531",
    "lineb.setNoVideo": "\u8bbe\u4e3a\u65e0\u753b\u9762\u8def\u7531",
    "lineb.micCheck": "\u9ea6\u514b\u98ce\u6743\u9650",
    "lineb.profile": "\u7ebf\u8def\u914d\u7f6e",
    "lineb.applyProfile": "\u5e94\u7528",
    "lineb.tts": "TTS \u7247\u6bb5",
    "lineb.registerTts": "\u767b\u8bb0",
    "lineb.micInput": "\u9ea6\u514b\u98ce\u8f93\u5165",
    "lineb.echoScore": "\u56de\u58f0\u5206\u6570",
    "lineb.submitMic": "\u63d0\u4ea4",
    "lineb.result": "\u7ed3\u679c",
    "lineb.micReady": "\u9ea6\u514b\u98ce\u53ef\u7528",
    "lineb.micBlocked": "\u9ea6\u514b\u98ce\u53d7\u9650",
    "lineb.routeReady": "\u65e0\u753b\u9762\u8def\u7531\u5df2\u5e94\u7528",
    "lineb.noProfiles": "\u6682\u65e0 profile",
    "livekit.room": "LiveKit \u623f\u95f4",
    "livekit.roomId": "\u623f\u95f4",
    "livekit.identity": "\u8eab\u4efd",
    "livekit.mint": "\u751f\u6210 Web Token",
    "livekit.connectAudio": "\u8fde\u63a5\u97f3\u9891",
    "livekit.disconnect": "\u65ad\u5f00",
    "livekit.ready": "token \u5df2\u751f\u6210\uff0c\u53ef\u63a5\u6d4f\u89c8\u5668\u97f3\u9891\u5ba2\u6237\u7aef",
    "livekit.unavailable": "token mint \u4e0d\u53ef\u7528",
    "livekit.connecting": "\u6b63\u5728\u8fde\u63a5 LiveKit...",
    "livekit.connected": "\u97f3\u9891\u5df2\u8fde\u63a5",
    "livekit.disconnected": "\u97f3\u9891\u5df2\u65ad\u5f00",
    "livekit.remoteAudio": "\u8fdc\u7aef\u97f3\u9891\u5df2\u63a5\u5165",
    "livekit.needsToken": "\u5148\u751f\u6210 Web Token...",
    "livekit.importFailed": "LiveKit \u6d4f\u89c8\u5668\u5ba2\u6237\u7aef\u52a0\u8f7d\u5931\u8d25",
    "livekit.events": "\u8fde\u63a5\u4e8b\u4ef6",
    "livekit.transcripts": "\u8f6c\u5199\u8bb0\u5f55",
    "livekit.noEvents": "\u6682\u65e0 LiveKit \u4e8b\u4ef6\u3002",
    "livekit.noTranscripts": "\u5f53\u524d\u6d4f\u89c8\u5668\u4f1a\u8bdd\u6682\u65e0\u8f6c\u5199\u8bb0\u5f55\u3002",
    "livekit.reconnecting": "\u6b63\u5728\u91cd\u8fde...",
    "livekit.signalReconnecting": "\u4fe1\u4ee4\u6b63\u5728\u91cd\u8fde...",
    "livekit.reconnected": "\u97f3\u9891\u5df2\u91cd\u8fde",
    "livekit.signalConnected": "\u4fe1\u4ee4\u5df2\u8fde\u63a5",
    "livekit.stateChanged": "\u72b6\u6001\u53d8\u5316",
    "livekit.manualDisconnect": "\u624b\u52a8\u65ad\u5f00",
    "livekit.trackSubscribed": "\u8fdc\u7aef\u8f68\u9053\u5df2\u8ba2\u9605",
    "livekit.trackUnsubscribed": "\u8fdc\u7aef\u8f68\u9053\u5df2\u53d6\u6d88",
    "livekit.transcriptReceived": "\u6536\u5230\u8f6c\u5199",
    "livekit.final": "\u6700\u7ec8",
    "livekit.partial": "\u4e34\u65f6",
    "livekit.error": "LiveKit \u9519\u8bef",
    "livekit.tokenMinted": "token \u5df2\u751f\u6210",
    "canvas.label": "\u753b\u5e03\u72b6\u6001",
    "canvas.modules": "\u6a21\u5757",
    "canvas.refs": "\u5f15\u7528",
    "canvas.tools": "\u5de5\u5177",
    "canvas.workspaces": "\u5de5\u4f5c\u533a",
    "canvas.map": "\u753b\u5e03\u56fe",
    "canvas.activeWorkspace": "\u5f53\u524d\u5de5\u4f5c\u533a",
    "memory.label": "\u56fe\u8c31\u5feb\u7167",
    "memory.blackboard": "\u9ed1\u677f",
    "memory.intent": "IntentWorkspace",
    "memory.refs": "Refs",
    "memory.l2b": "L2-B",
    "memory.lanes": "\u8bb0\u5fc6\u901a\u9053",
    "memory.visualWorkspace": "\u53ef\u89c6\u5316\u5de5\u4f5c\u533a",
    "memory.opsCockpit": "\u8bb0\u5fc6\u64cd\u4f5c\u5de5\u4f5c\u53f0",
    "memory.liveHint": "\u505c\u7559\u5728\u8bb0\u5fc6\u9875\u65f6\u6bcf 5 \u79d2\u8f6e\u8be2\uff1b\u6682\u505c\u4f1a\u51bb\u7ed3\u753b\u9762\u3002",
    "memory.sourceBuckets": "\u6765\u6e90\u6c60",
    "memory.dsgState": "DSG \u72b6\u6001",
    "memory.buckets": "\u6c60",
    "memory.open": "\u6253\u5f00",
    "memory.waitingForNodes": "\u7b49\u5f85 L2-B \u8282\u70b9",
    "memory.selectedActions": "\u9009\u4e2d\u8282\u70b9\u64cd\u4f5c",
    "memory.directHint": "\u70b9\u51fb L2-B \u8282\u70b9\u540e\uff0c\u76f4\u63a5\u8349\u62df\u5b89\u5168\u64cd\u4f5c\u3002",
    "memory.useSelected": "\u4f7f\u7528\u9009\u4e2d",
    "memory.setEdgeFrom": "\u8bbe\u4e3a From",
    "memory.setEdgeTo": "\u8bbe\u4e3a To",
    "memory.edgeDirectHint": "\u7528\u4e24\u4e2a\u9009\u4e2d\u7684 L2-B \u8282\u70b9\uff0c\u6216\u76f4\u63a5\u7c98\u8d34 UUID\u3002",
    "memory.receipts": "\u56de\u6267",
    "memory.clearPreview": "\u6e05\u9664\u9884\u89c8",
    "memory.preview": "\u9884\u89c8",
    "memory.advancedDrafts": "\u9ad8\u7ea7\u8349\u7a3f",
    "memory.operatorSafe": "\u64cd\u4f5c\u5458\u5b89\u5168",
    "memory.obsidianSettingNode": "Obsidian \u8bbe\u5b9a\u8282\u70b9",
    "memory.advancedNotes": "\u5907\u6ce8",
    "memory.advancedHint": "\u539f\u59cb JSON \u548c\u771f\u5b9e\u5199\u5165\u4fdd\u6301\u5728\u663e\u5f0f operator \u8def\u5f84\u540e\uff1b\u4e3b\u5de5\u4f5c\u53f0\u53ea\u653e\u660e\u786e\u7684\u5b89\u5168\u5e72\u8dd1\u64cd\u4f5c\u3002",
    "memory.graphMap": "L2-B \u5730\u56fe",
    "memory.toolArtifacts": "\u5de5\u5177\u75d5\u8ff9",
    "memory.nodes": "\u8282\u70b9",
    "memory.edges": "\u8fb9",
    "memory.present": "{count} \u5df2\u5199\u5165",
    "memory.declared": "{count} \u5df2\u58f0\u660e",
    "memory.readOnly": "\u53ea\u8bfb\u5feb\u7167",
    "memory.noNodes": "\u7b49\u5f85 L2-B \u8282\u70b9",
    "memory.noArtifacts": "\u6682\u65e0\u6d3b\u8dc3\u75d5\u8ff9",
    "memory.blackboardKeys": "\u9ed1\u677f\u952e",
    "memory.blackboardActivity": "\u9ed1\u677f\u6d3b\u52a8",
    "memory.intentRefs": "Intent \u5f15\u7528",
    "memory.detail": "\u8bb0\u5fc6\u8be6\u60c5",
    "memory.sequence": "\u5e8f\u53f7 {count}",
    "memory.emptyKeys": "\u6682\u65e0\u5df2\u5199\u5165\u952e",
    "memory.emptyRefs": "\u6682\u65e0\u6682\u5b58\u5f15\u7528",
    "memory.topAttention": "\u9ad8\u6ce8\u610f\u8282\u70b9",
    "memory.scope": "\u8303\u56f4",
    "memory.writer": "\u5199\u5165\u65b9",
    "memory.expires": "\u8fc7\u671f",
    "memory.owner": "\u6240\u6709\u8005",
    "memory.linked": "\u5df2\u8fde\u63a5",
    "memory.liveSnapshot": "\u5b9e\u65f6\u5feb\u7167",
    "memory.noSelection": "\u9009\u62e9\u8282\u70b9\u3001\u952e\u6216\u5f15\u7528",
    "memory.graphPlaceholder": "L2-B \u6709\u8282\u70b9\u540e\u663e\u793a\u5b9e\u65f6\u56fe",
    "memory.edgeCount": "{count} \u6761\u8fb9",
    "memory.attention": "\u6ce8\u610f",
    "memory.kind": "\u7c7b\u578b",
    "memory.source": "\u6765\u6e90",
    "memory.confirmation": "\u786e\u8ba4",
    "memory.connections": "\u8fde\u63a5",
    "memory.generated": "\u751f\u6210\u4e8e {time}",
    "memory.operatorWorkbench": "\u64cd\u4f5c\u5de5\u4f5c\u53f0",
    "memory.l15Pool": "L1.5 \u6c60",
    "memory.operation": "\u64cd\u4f5c",
    "memory.payload": "Payload JSON",
    "memory.draftBucketOp": "\u6c60\u64cd\u4f5c\u8349\u7a3f",
    "memory.bucketDryRun": "\u6c60\u64cd\u4f5c\u5e72\u8dd1",
    "memory.bucketQuickHint": "\u6c60\u5feb\u6377\u8349\u7a3f",
    "memory.freeze": "\u51bb\u7ed3",
    "memory.unfreeze": "\u89e3\u51bb",
    "memory.clear": "\u6e05\u7a7a",
    "memory.pressure": "\u538b\u529b",
    "memory.profile": "Profile",
    "memory.labelField": "\u6807\u7b7e",
    "memory.draft": "\u8349\u7a3f",
    "memory.dryRun": "\u5e72\u8dd1",
    "memory.l2bCrud": "L2-B \u8282\u70b9 CRUD",
    "memory.draftNode": "\u8282\u70b9\u8349\u7a3f",
    "memory.createDryRun": "\u521b\u5efa\u5e72\u8dd1",
    "memory.targetUuid": "\u76ee\u6807 UUID",
    "memory.updateDryRun": "\u66f4\u65b0\u5e72\u8dd1",
    "memory.deleteUuid": "\u5220\u9664 UUID",
    "memory.deleteDryRun": "\u5220\u9664\u5e72\u8dd1",
    "memory.edgeDraft": "\u8fb9\u8349\u7a3f",
    "memory.draftEdge": "\u8fb9\u8349\u7a3f",
    "memory.edgeDryRun": "\u8fb9\u5e72\u8dd1",
    "memory.allKinds": "\u5168\u90e8\u7c7b\u578b",
    "memory.applyFilters": "\u5e94\u7528",
    "memory.bucket": "\u6c60",
    "memory.changed": "\u53d8\u66f4",
    "memory.noActivity": "\u6682\u65e0\u6d3b\u52a8",
    "memory.visible": "\u53ef\u89c1",
    "memory.hidden": "\u9690\u85cf {count}",
    "memory.crossCompartment": "\u8de8\u533a",
    "memory.graphModeAll": "\u5168\u56fe",
    "memory.graphModeSelected": "\u9009\u4e2d\u90bb\u57df",
    "memory.graphModeAttention": "\u9ad8\u6ce8\u610f\u529b",
    "memory.canvasOps": "\u753b\u5e03\u64cd\u4f5c",
    "memory.createPreview": "\u521b\u5efa\u9884\u89c8",
    "memory.grouped": "\u5df2\u5206\u7ec4",
    "memory.eventDriven": "\u4e8b\u4ef6",
    "memory.refLinks": "\u5f15\u7528\u8fde\u63a5",
    "runtime.label": "\u8fd0\u884c\u6001",
    "runtime.scheduler": "\u8c03\u5ea6\u5668",
    "runtime.nanobot": "Nanobot",
    "runtime.plans": "Plan",
    "runtime.agentTeam": "Agent Team",
    "runtime.blackboard": "\u9ed1\u677f",
    "runtime.collaboration": "\u534f\u4f5c",
    "runtime.activeTasks": "\u6d3b\u8dc3\u4efb\u52a1",
    "runtime.reports": "\u56de\u62a5",
    "runtime.channels": "\u901a\u9053",
    "runtime.routeOrder": "\u8def\u7531\u987a\u5e8f",
    "runtime.taskTypes": "\u4efb\u52a1\u7c7b\u578b",
    "runtime.currentPlan": "\u5f53\u524d Plan",
    "runtime.noTasks": "\u6682\u65e0\u6d3b\u8dc3\u4efb\u52a1",
    "runtime.noPlans": "\u6682\u65e0 Plan",
    "runtime.readOnly": "\u53ea\u8bfb\u8fd0\u884c\u5feb\u7167",
    "runtime.placeholder": "V1 \u5360\u4f4d",
    "runtime.triggerLab": "\u89e6\u53d1\u5668\u5b9e\u9a8c\u53f0",
    "runtime.triggerPalette": "\u89e6\u53d1\u5668\u5feb\u6377\u64cd\u4f5c",
    "runtime.triggerPaletteHint": "\u9884\u8bbe\u6309\u94ae\u653e\u5728\u4e0a\u65b9\uff1b\u539f\u59cb JSON \u53ea\u7528\u4e8e\u81ea\u5b9a\u4e49\u5e72\u8dd1\u4e8b\u4ef6\u3002",
    "runtime.rawEvent": "\u539f\u59cb\u4e8b\u4ef6",
    "runtime.draftEvent": "\u4e8b\u4ef6\u8349\u7a3f",
    "runtime.fireDryRun": "\u89e6\u53d1\u5e72\u8dd1",
    "runtime.messageCheck": "\u68c0\u67e5\u90ae\u4ef6",
    "runtime.messagePush": "\u65b0\u4fe1\u63a8\u9001\u6d4b\u8bd5",
    "runtime.llmPush": "\u63a8\u9001\u7ed9 LLM",
    "runtime.schedulerTick": "\u8c03\u5ea6\u5668 Tick",
    "runtime.calendarTest": "\u65e5\u5386\u6d4b\u8bd5",
    "runtime.customEvent": "\u81ea\u5b9a\u4e49\u4e8b\u4ef6\u8349\u7a3f",
    "runtime.planGraph": "Plan \u56fe",
    "runtime.channelFlow": "\u901a\u9053\u6d41",
    "runtime.safeSurface": "\u5b89\u5168\u8868\u9762",
    "runtime.deps": "\u4f9d\u8d56",
    "runtime.result": "\u7ed3\u679c",
    "runtime.critical": "\u5173\u952e",
    "runtime.ready": "\u5c31\u7eea",
    "runtime.blocked": "\u963b\u585e",
    "runtime.stepDetail": "\u6b65\u9aa4\u8be6\u60c5",
    "runtime.expectedTool": "\u5de5\u5177",
    "runtime.nanobotTask": "Nanobot",
    "runtime.started": "\u5f00\u59cb",
    "runtime.completed": "\u5b8c\u6210",
    "runtime.error": "\u9519\u8bef",
    "graphiti.title": "Graphiti",
    "graphiti.label": "\u8bb0\u5fc6\u6838\u5fc3",
    "graphiti.status": "\u72b6\u6001",
    "graphiti.partitions": "\u5206\u533a",
    "graphiti.search": "\u641c\u7d22",
    "graphiti.query": "\u67e5\u8be2",
    "graphiti.partition": "\u5206\u533a",
    "graphiti.limit": "\u4e0a\u9650",
    "graphiti.runSearch": "\u641c\u7d22",
    "graphiti.results": "\u7ed3\u679c",
    "graphiti.episodeDraft": "Episode \u8349\u7a3f",
    "graphiti.episodeName": "\u540d\u79f0",
    "graphiti.episodeBody": "\u5185\u5bb9",
    "graphiti.draft": "\u8349\u7a3f",
    "graphiti.dryRun": "\u5e72\u8dd1",
    "graphiti.available": "\u53ef\u7528",
    "graphiti.unavailable": "\u53ef\u9009\u4f9d\u8d56\u7f3a\u5931",
    "graphiti.noPartitions": "\u6682\u65e0\u5206\u533a",
    "graphiti.noResults": "\u6682\u65e0\u7ed3\u679c",
    "graphiti.operatorNote": "\u5199\u5165\u9ed8\u8ba4\u4fdd\u6301 dry-run\uff0c\u53ea\u6709\u663e\u5f0f\u5f00\u542f operator \u6a21\u5f0f\u540e\u624d\u6267\u884c\u771f\u5199\u3002",
  },
};

const state = {
  activeView: "ops",
  paused: false,
  refreshMs: 15000,
  memoryRefreshMs: 5000,
  timer: null,
  language: initialLanguage(),
  config: null,
  lastEnvelope: null,
  lastHealth: null,
  appCanvas: null,
  lineProfiles: [],
  activeLineProfileId: "",
  linebResult: null,
  liveKitConfig: null,
  liveKitToken: null,
  liveKitTokenPayload: null,
  liveKitClientModule: null,
  liveKitRoom: null,
  liveKitManualDisconnect: false,
  liveKitEvents: [],
  liveKitTranscripts: [],
  remoteAudioElements: [],
  runtimeMonitor: null,
  runtimeSelectedStep: null,
  triggerCatalog: null,
  triggerReceipt: null,
  memoryState: null,
  memoryPrevious: null,
  memoryDiff: {
    l2bNodes: new Set(),
    blackboardKeys: new Set(),
    intentRefs: new Set(),
  },
  memoryDiffIds: new Set(),
  memoryGraphMode: "all",
  memoryFilters: {
    kind: "",
    source: "",
    bucket: "",
    minAttention: 0,
  },
  l15Pool: null,
  memoryOpsReceipt: null,
  memoryDraftPreview: {
    nodes: [],
    edges: [],
    deleteIds: new Set(),
    updateIds: new Set(),
  },
  memorySelected: null,
  graphitiStatus: null,
  graphitiSearch: null,
  graphitiDraft: null,
  blackboardActivity: null,
};

const liveKitClientUrls = [
  "https://cdn.jsdelivr.net/npm/livekit-client@2.18.10/dist/livekit-client.esm.mjs",
  "https://unpkg.com/livekit-client@2.18.10/dist/livekit-client.esm.mjs",
];

const $ = (id) => document.getElementById(id);

function initialLanguage() {
  const queryLang = new URLSearchParams(window.location.search).get("lang");
  if (queryLang === "zh" || queryLang === "en") {
    localStorage.setItem("parrot.console.language", queryLang);
    return queryLang;
  }
  const stored = localStorage.getItem("parrot.console.language");
  if (stored === "zh" || stored === "en") return stored;
  return navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
}

function t(key, params = {}) {
  const dictionary = dictionaries[state.language] || dictionaries.en;
  const template = dictionary[key] || dictionaries.en[key] || key;
  return Object.entries(params).reduce(
    (out, [name, value]) => out.replaceAll(`{${name}}`, String(value)),
    template,
  );
}

function text(value, fallback = "-") {
  if (value === null || value === undefined || value === "") return fallback;
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function errorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}

async function readJsonResponse(response, label = "") {
  const source = label || response.url || "request";
  const contentType = response.headers.get("content-type") || "";
  let body = null;

  if (contentType.includes("application/json")) {
    try {
      body = await response.json();
    } catch (error) {
      throw new Error(`${source}: invalid JSON (${errorMessage(error)})`);
    }
  } else {
    let raw = "";
    try {
      raw = await response.text();
    } catch (error) {
      raw = errorMessage(error);
    }
    body = raw ? { detail: raw } : {};
  }

  if (!response.ok) {
    const detail =
      typeof body === "object" && body
        ? body.detail || body.message || body.error
        : body;
    const statusText = response.statusText ? ` ${response.statusText}` : "";
    throw new Error(`${source}: ${response.status}${statusText}${detail ? ` - ${text(detail)}` : ""}`);
  }

  return body;
}

function formatTime(epochSeconds) {
  if (!epochSeconds) return t("empty.never");
  return new Date(epochSeconds * 1000).toLocaleTimeString();
}

function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  $("languageSelect").value = state.language;
  $("pauseButton").textContent = state.paused ? t("actions.resume") : t("actions.pause");
  renderViewTitle();
  if (!state.lastEnvelope) {
    $("lastFetch").textContent = t("last.waiting");
    $("connectionDetail").textContent = t("empty.noData");
  }
  if (state.config) renderConfig(state.config);
  if (state.lastEnvelope) {
    renderHealth(state.lastHealth);
    renderEnvelope(state.lastEnvelope, 0, false);
  }
  renderLiveKitEvents();
  renderLiveKitTranscripts();
  if (state.lineProfiles.length) renderLineProfiles();
  if (state.linebResult) renderLinebResult(state.linebResult);
  if (state.appCanvas) renderCanvas(state.appCanvas);
  if (state.runtimeMonitor) renderRuntimeMonitor(state.runtimeMonitor);
  if (state.triggerCatalog) renderTriggerLab(state.triggerCatalog);
  if (state.triggerReceipt) renderTriggerReceipt(state.triggerReceipt);
  if (state.memoryState) renderMemoryState(state.memoryState);
  if (state.l15Pool) renderL15Pool(state.l15Pool);
  if (state.blackboardActivity) renderMemoryBlackboardActivity(state.blackboardActivity);
  if (state.memoryOpsReceipt) renderMemoryOpsReceipt(state.memoryOpsReceipt);
  if (state.graphitiStatus) renderGraphitiStatus(state.graphitiStatus);
  if (state.graphitiSearch) renderGraphitiSearch(state.graphitiSearch);
  if (state.graphitiDraft) renderGraphitiDraft(state.graphitiDraft);
}

function renderViewTitle() {
  $("viewTitle").textContent =
    state.activeView === "lineb"
      ? t("lineb.title")
      : state.activeView === "runtime"
        ? t("runtime.title")
        : state.activeView === "canvas"
          ? t("canvas.title")
          : state.activeView === "memory"
            ? t("memory.title")
            : state.activeView === "graphiti"
              ? t("graphiti.title")
              : t("ops.title");
}

async function loadConfig() {
  const response = await fetch("/api/console/config");
  const config = await readJsonResponse(response, "/api/console/config");
  state.config = config;
  state.refreshMs = Math.max(5, Number(config.refresh_interval_s || 15)) * 1000;
  renderConfig(config);
}

function renderConfig(config) {
  $("authMode").textContent = t("auth.mode", { mode: config.orchestrator_auth_mode });
  $("orchUrl").textContent = t("auth.orchestrator", { url: config.orchestrator_base_url });
}

async function loadStatus() {
  const started = Date.now();
  setLoading(true);
  try {
    const [healthResponse, statusResponse] = await Promise.all([
      fetch("/api/orchestrator/health"),
      fetch("/api/orchestrator/status"),
    ]);
    const health = await readJsonResponse(healthResponse, "/api/orchestrator/health");
    const envelope = await readJsonResponse(statusResponse, "/api/orchestrator/status");
    renderHealth(health);
    renderEnvelope(envelope, Date.now() - started);
  } catch (error) {
    renderHealth(null);
    renderEnvelope({
      ok: false,
      state: "error",
      upstream: {},
      detail: { message: error instanceof Error ? error.message : String(error) },
      summary: {},
      status: null,
    });
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  $("refreshButton").disabled = isLoading;
  $("refreshButton").textContent = isLoading ? t("actions.loading") : t("actions.refresh");
}

function renderHealth(health) {
  state.lastHealth = health;
  const ok = Boolean(health?.ok);
  setLightInNode("nodeOrchestrator", ok ? "good" : "bad");
  setEdgeState("edgeHealth", ok ? "good" : "bad");
  $("orchestratorHealthText").textContent = ok
    ? t("topology.healthOk")
    : t("topology.healthMissing");
}

function renderEnvelope(envelope, durationMs = 0, remember = true) {
  if (remember) state.lastEnvelope = envelope;
  const status = envelope.status || {};
  const summary = envelope.summary || {};
  const upstream = envelope.upstream || {};
  const stateLabel = envelope.state || "unknown";
  const fetchedAt = upstream.fetched_at || Date.now() / 1000;

  const statusClass = classForState(stateLabel);
  setLight("overallLight", statusClass);
  $("connectionState").textContent = t(`states.${stateLabel}`) || stateLabel;
  $("connectionDetail").textContent = connectionDetail(envelope);
  $("lastFetch").textContent = t("last.fetched", {
    time: formatTime(fetchedAt),
    ms: durationMs,
  });

  const online = summary.online_processes ?? 0;
  const offline = summary.offline_processes ?? 0;
  const warnings = summary.warning_count ?? 0;
  $("moduleCount").textContent = `${online} / ${offline}`;
  $("warningCount").textContent = String(warnings);
  $("driftState").textContent = summary.selection_drift
    ? t("states.drift")
    : t("states.aligned");
  setLight("moduleLight", online > 0 && offline === 0 ? "good" : online > 0 ? "warn" : "idle");
  setLight("warningLight", warnings > 0 ? "warn" : "good");
  setLight("driftLight", summary.selection_drift ? "warn" : "good");

  const processes = Array.isArray(status.processes) ? status.processes : [];
  renderModules(processes);
  renderKv("runtimeConfig", status.runtime_config || {});
  renderKv("brainSnapshot", status.brain_runtime_snapshot || {});
  renderContainers(status.containers);
  renderWarnings(Array.isArray(status.warnings) ? status.warnings : []);
  renderTopology(envelope, summary);

  setPill("moduleTableState", modulePillState(summary));
  setPill("brainState", Object.keys(status.brain_runtime_snapshot || {}).length ? "good" : "");
  setPill("containerState", summary.containers_unavailable ? "warn" : "good");
  setPill("warningState", warnings > 0 ? "warn" : "good");
}

function connectionDetail(envelope) {
  const upstream = envelope.upstream || {};
  if (envelope.state === "unauthorized" && upstream.auth_mode === "dev-open") {
    return t("auth.secretMissing");
  }
  const detailText = envelope.detail?.message || envelope.detail?.error || "";
  if (!upstream.status_code) return text(detailText, "no upstream response");
  return `${upstream.status_code} from ${upstream.auth_mode || "unknown"}${
    detailText ? `; ${detailText}` : ""
  }`;
}

function renderTopology(envelope, summary) {
  const statusClass = classForState(envelope.state);
  setLightInNode("nodeConsole", "good");
  setLightInNode("nodeStatus", statusClass);
  setLightInNode("nodeModules", (summary.online_processes || 0) > 0 ? "good" : "warn");
  setEdgeState("edgeStatus", statusClass);
  setEdgeState("edgeModules", statusClass === "good" ? "good" : "warn");
  $("statusAuthText").textContent =
    envelope.state === "unauthorized"
      ? t("topology.statusDenied")
      : envelope.ok
        ? t("topology.statusOk")
        : t("topology.statusMissing");
  $("moduleTopologyText").textContent = t("topology.moduleCount", {
    count: summary.online_processes || 0,
  });
  setPill("topologyState", statusClass);
}

function classForState(statusState) {
  if (
    statusState === "connected" ||
    statusState === "ready" ||
    statusState === "ok" ||
    statusState === "success" ||
    statusState === "available" ||
    statusState === "user_turn" ||
    statusState === "approved" ||
    statusState === "complete" ||
    statusState === "done"
  ) {
    return "good";
  }
  if (
    statusState === "degraded" ||
    statusState === "unauthorized" ||
    statusState === "busy" ||
    statusState === "connecting" ||
    statusState === "reconnecting" ||
    statusState === "signalReconnecting" ||
    statusState === "agent_echo" ||
    statusState === "listening_uncertain" ||
    statusState === "uncertain" ||
    statusState === "draft" ||
    statusState === "awaiting_user_confirmation" ||
    statusState === "executing" ||
    statusState === "partial_complete" ||
    statusState === "pending" ||
    statusState === "dispatched" ||
    statusState === "running"
  ) {
    return "warn";
  }
  if (
    statusState === "offline" ||
    statusState === "error" ||
    statusState === "blocked" ||
    statusState === "blocked_mic" ||
    statusState === "failed" ||
    statusState === "cancelled"
  ) {
    return "bad";
  }
  return "idle";
}

function setLight(id, statusClass) {
  const el = $(id);
  if (!el) return;
  const small = el.classList.contains("small") ? " small" : "";
  el.className = `status-light${small} ${statusClass || "idle"}`.trim();
}

function setLightInNode(id, statusClass) {
  const node = $(id);
  if (!node) return;
  const light = node.querySelector(".status-light");
  if (light) {
    const small = light.classList.contains("small") ? " small" : "";
    light.className = `status-light${small} ${statusClass || "idle"}`.trim();
  }
}

function setEdgeState(id, statusClass) {
  const el = $(id);
  if (!el) return;
  el.className = `topology-edge ${statusClass || ""}`.trim();
}

function modulePillState(summary) {
  if ((summary.offline_processes || 0) > 0) return "bad";
  if ((summary.online_processes || 0) > 0) return "good";
  return "";
}

function setPill(id, statusClass, label = null) {
  const el = $(id);
  if (!el) return;
  el.className = `pill ${statusClass || ""}`.trim();
  if (label !== null) {
    el.textContent = label;
    return;
  }
  const labels = {
    moduleTableState:
      statusClass === "bad"
        ? t("pills.degraded")
        : statusClass === "good"
          ? t("pills.online")
          : t("pills.empty"),
    topologyState:
      statusClass === "bad"
        ? t("pills.degraded")
        : statusClass === "good"
          ? t("states.connected")
          : statusClass === "warn"
            ? t("states.degraded")
            : t("pills.checking"),
  };
  if (labels[id]) el.textContent = labels[id];
}

function renderModules(processes) {
  renderModuleMap(processes);
  const rows = $("moduleRows");
  rows.innerHTML = "";
  if (!processes.length) {
    rows.innerHTML = `<tr><td class="empty" colspan="6">${t("empty.noModuleHeartbeat")}</td></tr>`;
    return;
  }
  rows.innerHTML = processes
    .map((item) => {
      const stale = typeof item.stale_seconds === "number" ? `${item.stale_seconds.toFixed(1)}s` : "-";
      const dot = item.online ? "good" : "bad";
      return `<tr>
        <td>${escapeHtml(text(item.module_id))}</td>
        <td><span class="state-dot ${dot}"></span>${
          item.online ? t("states.online") : t("states.offlineShort")
        }</td>
        <td>${escapeHtml(text(item.module_type))}</td>
        <td>${escapeHtml(text(item.layers))}</td>
        <td>${escapeHtml(stale)}</td>
        <td>${escapeHtml(text(item.warning, ""))}</td>
      </tr>`;
    })
    .join("");
}

function renderModuleMap(processes) {
  const map = $("moduleMap");
  const items = processes.length
    ? processes
    : [
        { module_id: "brain", module_type: "Brain", online: false },
        { module_id: "scheduler", module_type: "Scheduler", online: false },
        { module_id: "nanobot-worker", module_type: "Nanobot", online: false },
        { module_id: "graphiti", module_type: "Memory", online: false },
        { module_id: "unity-app", module_type: "Unity", online: false },
        { module_id: "a10", module_type: "Vision/ECS", online: false },
      ];
  map.innerHTML = items
    .map((item) => {
      const light = item.online ? "good" : processes.length ? "bad" : "idle";
      const placeholder = processes.length ? "" : " placeholder";
      const note = processes.length
        ? item.online
          ? t("states.online")
          : t("states.offlineShort")
        : t("module.placeholder");
      return `<div class="module-card${placeholder}">
        <span class="status-light small ${light}"></span>
        <strong title="${escapeHtml(text(item.module_id))}">${escapeHtml(text(item.module_id))}</strong>
        <small>${escapeHtml(text(item.module_type))} - ${escapeHtml(note)}</small>
      </div>`;
    })
    .join("");
}

function renderKv(id, value) {
  const list = $(id);
  const entries = Object.entries(value || {});
  if (!entries.length) {
    list.innerHTML = `<dt class="empty">${t("pills.empty")}</dt><dd class="empty">${t("empty.noData")}</dd>`;
    return;
  }
  list.innerHTML = entries
    .map(([key, val]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(text(val))}</dd>`)
    .join("");
}

function renderContainers(containers) {
  const el = $("containers");
  if (!containers || (Array.isArray(containers) && !containers.length)) {
    el.textContent = t("empty.noContainer");
    return;
  }
  el.textContent = JSON.stringify(containers, null, 2);
}

function renderWarnings(warnings) {
  const list = $("warnings");
  if (!warnings.length) {
    list.innerHTML = `<li class="empty">${t("empty.noWarnings")}</li>`;
    return;
  }
  list.innerHTML = warnings.map((warning) => `<li>${escapeHtml(text(warning))}</li>`).join("");
}

async function loadLineBPanel() {
  setLoading(true);
  try {
    const [profilesResponse, modulesResponse, liveKitConfigResponse] = await Promise.all([
      fetch("/api/app/line-profiles"),
      fetch("/api/app/modules"),
      fetch("/api/livekit/config"),
    ]);
    const liveKitConfig = await readJsonResponse(liveKitConfigResponse, "/api/livekit/config");
    const profiles = await readJsonResponse(profilesResponse, "/api/app/line-profiles");
    const modules = await readJsonResponse(modulesResponse, "/api/app/modules");
    state.lineProfiles = Array.isArray(profiles) ? profiles : [];
    state.liveKitConfig = liveKitConfig;
    state.activeLineProfileId = extractActiveLineProfileId(modules) || state.activeLineProfileId;
    renderLineProfiles();
    renderLineBModules(modules);
    renderLiveKitConfig(liveKitConfig);
    $("lastFetch").textContent = t("last.fetched", {
      time: new Date().toLocaleTimeString(),
      ms: 0,
    });
  } finally {
    setLoading(false);
  }
}

function renderLineProfiles() {
  const select = $("lineProfileSelect");
  const lineBProfiles = state.lineProfiles.filter((profile) => profile.line_id === "line_b");
  const visibleProfiles = lineBProfiles.length ? lineBProfiles : state.lineProfiles;
  if (!visibleProfiles.length) {
    select.innerHTML = `<option value="">${t("lineb.noProfiles")}</option>`;
    setLight("profileLight", "warn");
    return;
  }
  select.innerHTML = visibleProfiles
    .map((profile) => {
      const id = text(profile.line_profile_id, "");
      const label = text(profile.display_name || profile.line_profile_id, id);
      return `<option value="${escapeHtml(id)}">${escapeHtml(label)}</option>`;
    })
    .join("");
  if (
    state.activeLineProfileId &&
    visibleProfiles.some((profile) => profile.line_profile_id === state.activeLineProfileId)
  ) {
    select.value = state.activeLineProfileId;
  }
  setLight("profileLight", "good");
}

function renderLineBModules(modules) {
  const voice = Array.isArray(modules)
    ? modules.find((module) => module.module_id === "voice_pipeline")
    : null;
  if (!voice) {
    $("voiceRouteState").textContent = t("empty.noData");
    return;
  }
  const stateText = text(voice.state, t("empty.noData"));
  state.activeLineProfileId = text(voice.metrics?.active_line_profile_id, state.activeLineProfileId);
  $("voiceRouteState").textContent = `${stateText} - ${text(voice.summary, "")}`;
  setLight("voiceRouteLight", classForState(voice.state));
}

function renderLiveKitConfig(config) {
  if (!config || !config.token_available) {
    setLight("livekitLight", "warn");
    $("livekitState").textContent = t("livekit.unavailable");
    return;
  }
  if (!$("livekitRoom").value) $("livekitRoom").value = text(config.room, "parrot-main");
  if ($("livekitRoom").value === "parrot-main" && config.room) $("livekitRoom").value = config.room;
  if (!$("livekitIdentity").value || $("livekitIdentity").value === "web-console") {
    $("livekitIdentity").value = `${config.web_identity_prefix || "web-console"}-${Date.now()}`;
  }
  if (hasFreshLiveKitToken()) {
    setLight("livekitLight", "good");
    $("livekitState").textContent = state.liveKitRoom
      ? `${t("livekit.connected")} (${text(state.liveKitTokenPayload.identity)})`
      : `${t("livekit.ready")} (${text(state.liveKitTokenPayload.identity)})`;
    return;
  }
  setLight("livekitLight", "idle");
  $("livekitState").textContent = `${text(config.url)} / ${text(config.room)}`;
}

function extractActiveLineProfileId(modules) {
  if (!Array.isArray(modules)) return "";
  const voice = modules.find((module) => module.module_id === "voice_pipeline");
  return text(voice?.metrics?.active_line_profile_id, "");
}

async function setNoVideoRoute() {
  const payload = await postJson("/api/app/lineb/audio-route", {
    input_route: "web_voice_lab",
    output_route: "web_audio",
    microphone_enabled: true,
    speaker_output_enabled: true,
    echo_handling_mode: "web_no_video",
    voiceprint_enabled: false,
    speaker_state: "web_no_video",
    source: "web_console.lineb_voice",
  });
  setLight("voiceRouteLight", "good");
  $("voiceRouteState").textContent = t("lineb.routeReady");
  renderLinebResult(payload);
}

async function checkMicrophone() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    stream.getTracks().forEach((track) => track.stop());
    setLight("voiceRouteLight", "good");
    renderLinebResult({ browser_mic: "available" });
    $("voiceRouteState").textContent = t("lineb.micReady");
  } catch (error) {
    setLight("voiceRouteLight", "bad");
    renderLinebResult({
      browser_mic: "blocked_mic",
      message: error instanceof Error ? error.message : String(error),
    });
    $("voiceRouteState").textContent = t("lineb.micBlocked");
  }
}

async function applyLineProfile() {
  const selected = $("lineProfileSelect").value;
  if (!selected) return;
  const payload = await postJson("/api/app/line-profiles/apply", {
    line_profile_id: selected,
  });
  setLight("profileLight", "good");
  renderLinebResult(payload);
}

async function registerTtsSegment() {
  const payload = await postJson("/api/app/lineb/tts-segment", {
    text_summary: $("ttsText").value,
    duration_s: 1.0,
    tts_voice: "web_console",
    conversation_turn_id: `web-${Date.now()}`,
  });
  renderLinebResult(payload);
}

async function submitMicInput() {
  const payload = await postJson("/api/app/lineb/mic-input", {
    asr_text: $("micText").value,
    echo_score: $("echoScore").value,
    duration_s: 1.0,
    speaker_label: "web_operator",
  });
  renderLinebResult(payload);
}

function renderLinebResult(payload) {
  const safePayload = redactSensitiveResult(payload);
  state.linebResult = safePayload;
  $("linebOutput").textContent = JSON.stringify(safePayload, null, 2);
  const label = payload.turn_decision || payload.status || payload.browser_mic || "ok";
  setPill("linebResultPill", classForState(label), text(label));
}

async function mintLiveKitToken() {
  const payload = await postJson("/api/livekit/web-token", {
    room: $("livekitRoom").value,
    identity: $("livekitIdentity").value,
  });
  state.liveKitToken = payload.token;
  state.liveKitTokenPayload = payload;
  setLight("livekitLight", "good");
  $("livekitState").textContent = `${t("livekit.ready")} (${text(payload.identity)})`;
  pushLiveKitEvent("livekit.tokenMinted", `${text(payload.room)} / ${text(payload.identity)}`, "good");
  renderLinebResult({
    status: "success",
    url: payload.url,
    room: payload.room,
    identity: payload.identity,
    expires_at: payload.expires_at,
    token_length: payload.token ? payload.token.length : 0,
    token: payload.token,
  });
  return payload;
}

async function connectLiveKitAudio() {
  if (state.liveKitRoom) return;
  state.liveKitManualDisconnect = false;
  $("connectLiveKitButton").disabled = true;
  $("disconnectLiveKitButton").disabled = true;
  setLight("livekitLight", "warn");
  $("livekitState").textContent = t(state.liveKitToken ? "livekit.connecting" : "livekit.needsToken");
  pushLiveKitEvent("livekit.connecting", "", "warn");
  try {
    const [{ Room, RoomEvent, Track }, session] = await Promise.all([
      loadLiveKitClient(),
      ensureLiveKitToken(),
    ]);
    const room = new Room({ adaptiveStream: false, dynacast: false });
    state.liveKitRoom = room;
    onLiveKitRoomEvent(room, RoomEvent, "ConnectionStateChanged", (connectionState) => {
      const stateText = text(connectionState, "");
      pushLiveKitEvent("livekit.stateChanged", stateText, classForState(stateText));
      if (stateText === "reconnecting" || stateText === "signalReconnecting") {
        setLight("livekitLight", "warn");
        $("livekitState").textContent = `${t("livekit.stateChanged")}: ${stateText}`;
      }
    });
    onLiveKitRoomEvent(room, RoomEvent, "SignalReconnecting", () => {
      setLight("livekitLight", "warn");
      $("livekitState").textContent = t("livekit.signalReconnecting");
      pushLiveKitEvent("livekit.signalReconnecting", "", "warn");
    });
    onLiveKitRoomEvent(room, RoomEvent, "SignalConnected", () => {
      pushLiveKitEvent("livekit.signalConnected", "", "good");
    });
    onLiveKitRoomEvent(room, RoomEvent, "Reconnecting", () => {
      setLight("livekitLight", "warn");
      $("livekitState").textContent = t("livekit.reconnecting");
      pushLiveKitEvent("livekit.reconnecting", "", "warn");
    });
    onLiveKitRoomEvent(room, RoomEvent, "Reconnected", () => {
      attachExistingRemoteAudio(room, Track);
      setLight("livekitLight", "good");
      $("livekitState").textContent = `${t("livekit.reconnected")} (${text(session.identity)})`;
      $("disconnectLiveKitButton").disabled = false;
      pushLiveKitEvent("livekit.reconnected", text(session.identity), "good");
    });
    onLiveKitRoomEvent(room, RoomEvent, "TrackSubscribed", (track, _publication, participant) => {
      if (isAudioTrack(track, Track)) attachRemoteAudio(track, participant);
    });
    onLiveKitRoomEvent(room, RoomEvent, "TrackUnsubscribed", (track) => {
      detachRemoteAudio(track);
      pushLiveKitEvent("livekit.trackUnsubscribed", "", "idle");
    });
    onLiveKitRoomEvent(room, RoomEvent, "TranscriptionReceived", (segments, participant) => {
      appendLiveKitTranscripts(segments, participant);
      pushLiveKitEvent("livekit.transcriptReceived", text(participant?.identity, "remote"), "good");
    });
    onLiveKitRoomEvent(room, RoomEvent, "DataReceived", (payload, participant, _kind, topic) => {
      if (topic !== "lk.transcription") return;
      const transcript = decodeLiveKitDataPayload(payload);
      if (!transcript) return;
      appendLiveKitTranscripts([{ text: transcript, final: true, source: topic }], participant);
      pushLiveKitEvent("livekit.transcriptReceived", topic, "good");
    });
    onLiveKitRoomEvent(room, RoomEvent, "Disconnected", (reason) => {
      const manual = state.liveKitManualDisconnect;
      cleanupLiveKitAudioUi();
      setLight("livekitLight", manual ? "idle" : "bad");
      $("livekitState").textContent = `${t("livekit.disconnected")}${
        reason ? ` - ${text(reason, "")}` : ""
      }`;
      pushLiveKitEvent("livekit.disconnected", text(reason, ""), manual ? "idle" : "bad");
      state.liveKitManualDisconnect = false;
    });

    await room.connect(session.url, session.token, { autoSubscribe: true });
    if (typeof room.startAudio === "function") await room.startAudio();
    await room.localParticipant.setMicrophoneEnabled(true);
    attachExistingRemoteAudio(room, Track);
    setLight("livekitLight", "good");
    $("livekitState").textContent = `${t("livekit.connected")} (${text(session.identity)})`;
    $("disconnectLiveKitButton").disabled = false;
    pushLiveKitEvent("livekit.connected", text(session.identity), "good");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    pushLiveKitEvent("livekit.error", message, "bad");
    if (state.liveKitRoom) state.liveKitRoom.disconnect();
    cleanupLiveKitAudioUi();
    setLight("livekitLight", "bad");
    $("livekitState").textContent = message;
    state.liveKitManualDisconnect = false;
  } finally {
    if (!state.liveKitRoom) $("connectLiveKitButton").disabled = false;
  }
}

function disconnectLiveKitAudio() {
  if (state.liveKitRoom) {
    state.liveKitManualDisconnect = true;
    $("disconnectLiveKitButton").disabled = true;
    $("livekitState").textContent = t("livekit.manualDisconnect");
    pushLiveKitEvent("livekit.manualDisconnect", "", "idle");
    state.liveKitRoom.disconnect();
    return;
  }
  cleanupLiveKitAudioUi();
  setLight("livekitLight", "idle");
  $("livekitState").textContent = t("livekit.disconnected");
  pushLiveKitEvent("livekit.disconnected", "", "idle");
}

function onLiveKitRoomEvent(room, RoomEvent, name, handler) {
  const eventName = RoomEvent?.[name];
  if (eventName) room.on(eventName, handler);
}

function pushLiveKitEvent(key, detail = "", statusClass = "idle") {
  state.liveKitEvents = [
    {
      at: new Date().toLocaleTimeString(),
      key,
      detail: text(detail, ""),
      statusClass: statusClass || "idle",
    },
    ...state.liveKitEvents,
  ].slice(0, 16);
  renderLiveKitEvents();
}

function renderLiveKitEvents() {
  const list = $("livekitEvents");
  if (!list) return;
  if (!state.liveKitEvents.length) {
    list.innerHTML = `<span class="empty">${t("livekit.noEvents")}</span>`;
    return;
  }
  list.innerHTML = state.liveKitEvents
    .map((item) => {
      const detail = item.detail ? `<p>${escapeHtml(item.detail)}</p>` : "";
      return `<article class="livekit-row ${escapeHtml(item.statusClass)}">
        <header>
          <strong>${escapeHtml(t(item.key))}</strong>
          <time>${escapeHtml(item.at)}</time>
        </header>
        ${detail}
      </article>`;
    })
    .join("");
}

function appendLiveKitTranscripts(segments, participant) {
  const nextRows = normalizeLiveKitSegments(segments, participant);
  if (!nextRows.length) return;
  state.liveKitTranscripts = [...nextRows.reverse(), ...state.liveKitTranscripts].slice(0, 32);
  renderLiveKitTranscripts();
}

function normalizeLiveKitSegments(segments, participant) {
  const rawSegments = Array.isArray(segments) ? segments : [segments];
  return rawSegments
    .map((segment) => {
      const body =
        segment?.text ||
        segment?.finalText ||
        segment?.transcript ||
        segment?.message ||
        (typeof segment === "string" ? segment : "");
      if (!body) return null;
      return {
        at: new Date().toLocaleTimeString(),
        participant: text(
          participant?.identity || segment?.participantIdentity || segment?.speaker || segment?.role,
          "remote",
        ),
        body: text(body, ""),
        final: Boolean(segment?.final ?? segment?.isFinal ?? segment?.finalized ?? true),
        source: text(segment?.source, ""),
      };
    })
    .filter(Boolean);
}

function renderLiveKitTranscripts() {
  const list = $("livekitTranscripts");
  if (!list) return;
  if (!state.liveKitTranscripts.length) {
    list.innerHTML = `<span class="empty">${t("livekit.noTranscripts")}</span>`;
    return;
  }
  list.innerHTML = state.liveKitTranscripts
    .map((item) => {
      const mode = item.final ? t("livekit.final") : t("livekit.partial");
      const source = item.source ? ` / ${escapeHtml(item.source)}` : "";
      return `<article class="livekit-row good">
        <header>
          <strong>${escapeHtml(item.participant)}</strong>
          <small>${escapeHtml(mode)}${source} - ${escapeHtml(item.at)}</small>
        </header>
        <p>${escapeHtml(item.body)}</p>
      </article>`;
    })
    .join("");
}

function decodeLiveKitDataPayload(payload) {
  try {
    const asText =
      typeof payload === "string" ? payload : new TextDecoder("utf-8").decode(payload || new Uint8Array());
    if (!asText) return "";
    try {
      const parsed = JSON.parse(asText);
      return text(parsed.text || parsed.transcript || parsed.message || parsed.content, "");
    } catch {
      return asText;
    }
  } catch {
    return "";
  }
}

async function loadLiveKitClient() {
  if (state.liveKitClientModule) return state.liveKitClientModule;
  let lastError = null;
  for (const url of liveKitClientUrls) {
    try {
      state.liveKitClientModule = await import(url);
      return state.liveKitClientModule;
    } catch (error) {
      lastError = error;
    }
  }
  throw new Error(
    `${t("livekit.importFailed")}: ${lastError instanceof Error ? lastError.message : String(lastError)}`,
  );
}

async function ensureLiveKitToken() {
  const payload = hasFreshLiveKitToken() ? state.liveKitTokenPayload : await mintLiveKitToken();
  return {
    token: payload.token,
    url: payload.url || state.liveKitConfig?.url,
    room: payload.room || $("livekitRoom").value,
    identity: payload.identity || $("livekitIdentity").value,
  };
}

function hasFreshLiveKitToken() {
  if (!state.liveKitToken || !state.liveKitTokenPayload) return false;
  const expiresAt = Number(state.liveKitTokenPayload.expires_at || 0);
  return !expiresAt || expiresAt - Math.floor(Date.now() / 1000) > 20;
}

function attachExistingRemoteAudio(room, Track) {
  room.remoteParticipants.forEach((participant) => {
    participant.trackPublications.forEach((publication) => {
      if (publication.track && publication.isSubscribed && isAudioTrack(publication.track, Track)) {
        attachRemoteAudio(publication.track, participant);
      }
    });
  });
}

function isAudioTrack(track, Track) {
  const audioKind = Track?.Kind?.Audio || "audio";
  return track?.kind === audioKind || track?.kind === "audio";
}

function attachRemoteAudio(track, participant) {
  if (state.remoteAudioElements.some((item) => item.track === track)) return;
  const element = track.attach();
  element.autoplay = true;
  element.controls = false;
  element.dataset.participantIdentity = text(participant?.identity, "remote");
  $("remoteAudioMount").appendChild(element);
  state.remoteAudioElements.push({ track, element });
  $("livekitState").textContent = `${t("livekit.remoteAudio")} - ${text(participant?.identity, "remote")}`;
  pushLiveKitEvent("livekit.trackSubscribed", text(participant?.identity, "remote"), "good");
}

function detachRemoteAudio(track = null) {
  state.remoteAudioElements = state.remoteAudioElements.filter((item) => {
    if (track && item.track !== track) return true;
    if (typeof item.track.detach === "function") {
      item.track.detach().forEach((element) => element.remove());
    } else {
      item.element.remove();
    }
    return false;
  });
}

function cleanupLiveKitAudioUi() {
  detachRemoteAudio();
  $("remoteAudioMount").innerHTML = "";
  $("connectLiveKitButton").disabled = false;
  $("disconnectLiveKitButton").disabled = true;
  state.liveKitRoom = null;
}

function redactSensitiveResult(payload) {
  const clone = { ...(payload || {}) };
  if (clone.token) {
    clone.token = `<redacted ${String(clone.token).length} chars>`;
  }
  return clone;
}

async function loadCanvasPanel() {
  setLoading(true);
  try {
    const response = await fetch("/api/app/canvas");
    const payload = await readJsonResponse(response, "/api/app/canvas");
    renderCanvas(payload);
    $("lastFetch").textContent = t("last.fetched", {
      time: new Date().toLocaleTimeString(),
      ms: 0,
    });
  } finally {
    setLoading(false);
  }
}

function renderCanvas(canvas) {
  state.appCanvas = canvas;
  const modules = Array.isArray(canvas.module_statuses) ? canvas.module_statuses : [];
  const notes = Array.isArray(canvas.paper_notes) ? canvas.paper_notes : [];
  const photos = Array.isArray(canvas.photo_refs) ? canvas.photo_refs : [];
  const tools = Array.isArray(canvas.tool_cabinet) ? canvas.tool_cabinet : [];
  const workspaces = Array.isArray(canvas.workspaces) ? canvas.workspaces : [];
  const activeWorkspace = text(canvas.active_workspace_id, "workdesk");

  setLight("canvasLight", "good");
  $("canvasTitle").textContent = activeWorkspace;
  $("canvasSummary").textContent = t("canvas.activeWorkspace");
  $("canvasModuleCount").textContent = String(modules.length);
  $("canvasRefCount").textContent = String(notes.length + photos.length);
  $("canvasToolCount").textContent = String(tools.length);
  setPill("workspacePill", workspaces.length ? "good" : "", String(workspaces.length));

  renderWorkspaceRail(workspaces, activeWorkspace);
  renderCanvasGraph({ modules, notes, photos, tools, activeWorkspace });
}

function renderWorkspaceRail(workspaces, activeWorkspace) {
  const rail = $("workspaceRail");
  if (!workspaces.length) {
    rail.innerHTML = `<span class="empty">${t("empty.noData")}</span>`;
    return;
  }
  rail.innerHTML = workspaces
    .map((workspace) => {
      const id = text(workspace.workspace_id, "");
      const label = text(workspace.display_name || workspace.workspace_id, id);
      const active = id === activeWorkspace ? " active" : "";
      return `<button class="workspace-chip${active}" type="button" data-workspace-id="${escapeHtml(id)}">
        ${escapeHtml(label)}
      </button>`;
    })
    .join("");
  rail.querySelectorAll("[data-workspace-id]").forEach((button) => {
    button.addEventListener("click", () => applyWorkspace(button.dataset.workspaceId));
  });
}

async function applyWorkspace(workspaceId) {
  const payload = await postJson("/api/app/workspace/apply", { workspace_id: workspaceId });
  await loadCanvasPanel();
  $("canvasSummary").textContent = `${t("canvas.activeWorkspace")} - ${text(payload.message, workspaceId)}`;
}

function renderCanvasGraph({ modules, notes, photos, tools, activeWorkspace }) {
  const graph = $("canvasGraph");
  const moduleCards = modules.map((module) =>
    canvasNode("module", module.module_id, module.state, classForState(module.state)),
  );
  const noteCards = notes.map((note) => canvasNode("note", note.title || note.ref_id, note.role, "warn"));
  const photoCards = photos.map((photo) => canvasNode("photo", photo.photo_id || photo.ref_id, photo.role, "warn"));
  const toolCards = tools.map((tool) => canvasNode("tool", tool.title || tool.tool_id, tool.state, "idle"));
  graph.innerHTML = [
    canvasNode("workspace", activeWorkspace, t("canvas.activeWorkspace"), "good"),
    ...moduleCards,
    ...noteCards,
    ...photoCards,
    ...toolCards,
  ].join("");
}

function canvasNode(kind, title, subtitle, light) {
  return `<article class="canvas-node ${escapeHtml(kind)}" data-kind="${escapeHtml(kind)}">
    <span class="status-light small ${escapeHtml(light || "idle")}"></span>
    <strong title="${escapeHtml(text(title))}">${escapeHtml(text(title))}</strong>
    <small>${escapeHtml(text(subtitle, kind))}</small>
  </article>`;
}

async function loadRuntimePanel() {
  setLoading(true);
  try {
    const [response, triggerResponse] = await Promise.all([
      fetch("/api/runtime/monitor"),
      fetch("/api/dsg/triggers/catalog"),
    ]);
    const payload = await readJsonResponse(response, "/api/runtime/monitor");
    const triggerPayload = await readJsonResponse(triggerResponse, "/api/dsg/triggers/catalog");
    renderRuntimeMonitor(payload);
    renderTriggerLab(triggerPayload);
    $("lastFetch").textContent = t("last.fetched", {
      time: new Date().toLocaleTimeString(),
      ms: 0,
    });
  } finally {
    setLoading(false);
  }
}

function renderRuntimeMonitor(payload) {
  state.runtimeMonitor = payload;
  const scheduler = payload.scheduler || {};
  const nanobot = payload.nanobot || {};
  const plans = payload.plans || {};
  const blackboard = payload.blackboard || {};
  const agentTeam = payload.agent_team || {};
  const collaboration = payload.collaboration || {};
  const nanobotStatus = nanobot.status || {};
  const activeTasks = Number(scheduler.active_task_count || 0);
  const activePlans = Number(plans.active_count || 0);
  const reportCount = Number(nanobot.report_count || 0);

  setLight("runtimeLight", activeTasks || activePlans || reportCount ? "good" : "idle");
  $("runtimeTitle").textContent = text(agentTeam.display_name, "CatMaid Team");
  $("runtimeSummary").textContent = `${t("runtime.readOnly")} - ${text(nanobotStatus.state, "idle")}`;
  $("runtimeTaskCount").textContent = String(activeTasks);
  $("runtimePlanCount").textContent = `${activePlans}/${text(plans.archived_count, 0)}`;
  $("runtimeReportCount").textContent = String(reportCount);
  setPill("runtimeReadPill", "good", t("pills.read"));
  setPill("runtimeSchedulerPill", activeTasks ? "good" : "", String(activeTasks));
  setPill("runtimePlanPill", activePlans ? "good" : "", String(activePlans));
  setPill("runtimeNanobotPill", classForState(nanobotStatus.state), text(nanobotStatus.state, "idle"));
  setPill("runtimeAgentPill", classForState(agentTeam.status), text(agentTeam.status, t("runtime.placeholder")));

  renderRuntimeLanes({ scheduler, nanobot, plans, blackboard, agentTeam });
  renderRuntimeScheduler(scheduler);
  renderRuntimePlans(plans);
  renderRuntimeNanobot(nanobot);
  renderRuntimeAgentTeam(agentTeam, collaboration);
}

function renderTriggerLab(payload) {
  state.triggerCatalog = payload;
  const triggers = Array.isArray(payload?.triggers) ? payload.triggers : [];
  setPill("triggerLabPill", triggers.length ? "good" : "", String(triggers.length));
  $("triggerCatalogList").innerHTML = triggers.length
    ? triggers
        .slice(0, 10)
        .map((item) => {
          const kinds = Array.isArray(item.kinds) ? item.kinds.join(", ") : "";
          const sample = Array.isArray(item.event_hints) && item.event_hints[0]
            ? JSON.stringify(item.event_hints[0])
            : "";
          return `<button type="button" class="compact-list-row" data-trigger-sample="${escapeHtml(sample)}">
            <strong>${escapeHtml(text(item.name))}</strong>
            <small>${escapeHtml(kinds || t("pills.empty"))} / ${escapeHtml(text(item.interval_seconds, 0))}s</small>
          </button>`;
        })
        .join("")
    : `<span class="empty">${t("empty.noData")}</span>`;
  document.querySelectorAll("[data-trigger-sample]").forEach((button) => {
    button.addEventListener("click", () => {
      const sample = button.dataset.triggerSample || "";
      if (sample) $("triggerEventJson").value = JSON.stringify(JSON.parse(sample), null, 2);
    });
  });
  if (!state.triggerReceipt) {
    $("triggerReceipt").textContent = "";
  }
}

function renderTriggerReceipt(payload) {
  state.triggerReceipt = payload;
  $("triggerReceipt").textContent = JSON.stringify(payload, null, 2);
  setPill("triggerLabPill", payload?.success ? "good" : "bad", text(payload?.action, t("pills.test")));
}

function readTriggerEvent() {
  const raw = $("triggerEventJson").value.trim();
  if (!raw) return { type: "web_console_test", source: "web_console" };
  try {
    return JSON.parse(raw);
  } catch (error) {
    return {
      type: "invalid_json",
      raw,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

function triggerPresetEvent(kind) {
  const now = new Date().toISOString();
  const presets = {
    llm_context_push: {
      type: "llm_context_push",
      source: "web_console",
      topic: "operator_test",
      message: "Web Console manual LLM context push dry-run.",
      created_at: now,
    },
    scheduler_tick: {
      type: "scheduler_tick",
      source: "web_console",
      reason: "operator_test",
      created_at: now,
    },
    calendar_event: {
      type: "calendar_event",
      source: "web_console",
      event_id: "web_calendar_test",
      title: "Web Console calendar trigger test",
      starts_at: now,
    },
    web_console_custom: {
      type: "web_console_custom",
      source: "web_console",
      note: "Custom DSG event draft from Web Console.",
      created_at: now,
    },
  };
  return presets[kind] || presets.web_console_custom;
}

async function draftTriggerPreset(kind) {
  $("triggerEventJson").value = JSON.stringify(triggerPresetEvent(kind), null, 2);
  await draftTriggerEvent();
}

async function draftTriggerEvent() {
  const payload = await postJson("/api/dsg/triggers/draft-event", {
    event: readTriggerEvent(),
    dry_run: true,
  });
  renderTriggerReceipt(payload);
}

async function fireTriggerDryRun() {
  const payload = await postJson("/api/dsg/triggers/fire-event", {
    event: readTriggerEvent(),
    dry_run: true,
    operator_mode: false,
  });
  renderTriggerReceipt(payload);
}

async function dispatchMessageCheckDryRun() {
  const payload = await postJson("/api/google/messages/check", {
    dry_run: true,
    operator_mode: false,
  });
  renderTriggerReceipt(payload);
}

async function pushMessageDryRun() {
  const payload = await postJson("/api/google/messages/push-test", {
    dry_run: true,
    operator_mode: false,
    subject: "Web Console message push test",
  });
  renderTriggerReceipt(payload);
}

function renderRuntimeLanes({ scheduler, nanobot, plans, blackboard, agentTeam }) {
  const lanes = [
    {
      id: "scheduler",
      label: t("runtime.scheduler"),
      count: text(scheduler.active_task_count, 0),
      detail: t("runtime.activeTasks"),
      light: (scheduler.active_task_count || 0) > 0 ? "good" : "idle",
    },
    {
      id: "nanobot",
      label: t("runtime.nanobot"),
      count: text(nanobot.report_count, 0),
      detail: t("runtime.reports"),
      light: (nanobot.report_count || 0) > 0 ? "good" : classForState(nanobot.status?.state),
    },
    {
      id: "plans",
      label: t("runtime.plans"),
      count: `${text(plans.active_count, 0)}/${text(plans.archived_count, 0)}`,
      detail: Object.keys(plans.state_counts || {}).join(", ") || t("runtime.noPlans"),
      light: (plans.active_count || 0) > 0 ? "good" : "idle",
    },
    {
      id: "blackboard",
      label: t("runtime.blackboard"),
      count: `${text(blackboard.present_count, 0)}/${text(blackboard.declared_count, 0)}`,
      detail: Object.keys(blackboard.present_by_scope || {}).join(", ") || t("pills.empty"),
      light: (blackboard.present_count || 0) > 0 ? "good" : "idle",
    },
    {
      id: "agent-team",
      label: t("runtime.agentTeam"),
      count: text(agentTeam.members?.length, 1),
      detail: text(agentTeam.display_name, "CatMaid Team"),
      light: classForState(agentTeam.status),
    },
  ];
  $("runtimeLanes").innerHTML = lanes
    .map((lane) => `<article class="memory-lane ${escapeHtml(lane.id)}">
      <span class="status-light small ${escapeHtml(lane.light)}"></span>
      <strong>${escapeHtml(lane.label)}</strong>
      <b>${escapeHtml(lane.count)}</b>
      <small>${escapeHtml(lane.detail)}</small>
    </article>`)
    .join("");
}

function renderRuntimeScheduler(scheduler) {
  const routeOrder = scheduler.router?.route_order || [];
  const channels = scheduler.channels || {};
  const activeTasks = Array.isArray(scheduler.active_tasks) ? scheduler.active_tasks : [];
  const taskTypes = scheduler.nanobot_task_types?.all || [];
  $("runtimeScheduler").innerHTML = [
    runtimeMiniSection(t("runtime.routeOrder"), routeOrder.join(" -> ") || "-"),
    runtimeMiniSection(t("runtime.channels"), Object.entries(channels).map(([k, v]) => `${k}: ${v}`).join("\n")),
    runtimeMiniSection(t("runtime.taskTypes"), taskTypes.join(", ")),
    runtimeMiniSection(
      t("runtime.activeTasks"),
      activeTasks.length
        ? activeTasks.map((task) => `${text(task.task_id)} / ${text(task.type)} / ${text(task.status)}`).join("\n")
        : t("runtime.noTasks"),
    ),
  ].join("");
}

function renderRuntimePlans(plans) {
  const rows = Array.isArray(plans.plans) ? plans.plans : [];
  if (!rows.length) {
    $("runtimePlans").innerHTML = `<span class="empty">${t("runtime.noPlans")}</span>`;
    return;
  }
  const selected = resolveRuntimeSelectedStep(rows);
  if (state.runtimeSelectedStep && !selected) state.runtimeSelectedStep = null;
  $("runtimePlans").innerHTML = rows
    .map((plan) => {
      const stepCounts = Object.entries(plan.step_state_counts || {})
        .map(([stateName, count]) => `${stateName}:${count}`)
        .join(", ");
      const links = [
        plan.intent_event_id ? `intent:${plan.intent_event_id}` : "",
        plan.episode_id ? `episode:${plan.episode_id}` : "",
        plan.staged_ref_id ? `ref:${plan.staged_ref_id}` : "",
      ].filter(Boolean).join(" / ");
      return `<article class="runtime-row plan-row">
        <span class="status-light small ${escapeHtml(classForState(plan.state))}"></span>
        <strong title="${escapeHtml(text(plan.title || plan.plan_id))}">${escapeHtml(text(plan.title || plan.plan_id))}</strong>
        <small>${escapeHtml(text(plan.state))} / ${escapeHtml(text(plan.step_count, 0))}${stepCounts ? ` / ${escapeHtml(stepCounts)}` : ""}</small>
        ${renderRuntimePlanDag(plan)}
        ${renderRuntimePlanStepDetail(plan)}
        ${links ? `<small class="runtime-row-links">${escapeHtml(links)}</small>` : ""}
      </article>`;
    })
    .join("");
  bindRuntimePlanStepButtons();
}

function renderRuntimePlanDag(plan) {
  const dag = plan.dag || {};
  const nodes = Array.isArray(dag.nodes) ? dag.nodes.slice(0, 8) : [];
  const edges = Array.isArray(dag.edges) ? dag.edges : [];
  if (!nodes.length) return "";
  const selectedStepId = state.runtimeSelectedStep?.planId === text(plan.plan_id, "") ? state.runtimeSelectedStep.stepId : "";
  const criticalIds = new Set(Array.isArray(dag.critical_step_ids) ? dag.critical_step_ids.map((id) => text(id, "")) : []);
  const readyIds = new Set(Array.isArray(dag.ready_step_ids) ? dag.ready_step_ids.map((id) => text(id, "")) : []);
  const blockedIds = new Set(Array.isArray(dag.blocked_step_ids) ? dag.blocked_step_ids.map((id) => text(id, "")) : []);
  const width = 360;
  const height = 116;
  const xStep = nodes.length > 1 ? (width - 52) / (nodes.length - 1) : 0;
  const positions = nodes.map((node, index) => ({
    node,
    x: Math.round(26 + xStep * index),
    y: 34 + (index % 2) * 40,
  }));
  const positionMap = new Map(positions.map((item) => [text(item.node.step_id), item]));
  const edgeMarkup = edges
    .filter((edge) => positionMap.has(text(edge.source)) && positionMap.has(text(edge.target)))
    .map((edge) => {
      const source = positionMap.get(text(edge.source));
      const target = positionMap.get(text(edge.target));
      const sourceId = text(edge.source);
      const targetId = text(edge.target);
      const active = selectedStepId && (sourceId === selectedStepId || targetId === selectedStepId) ? "selected" : "";
      const critical = criticalIds.has(sourceId) && criticalIds.has(targetId) ? "critical" : "";
      return `<path class="plan-edge ${active} ${critical}" d="M${source.x + 14} ${source.y} C${source.x + 48} ${source.y}, ${target.x - 48} ${target.y}, ${target.x - 14} ${target.y}" />`;
    })
    .join("");
  const nodeMarkup = positions
    .map((item, index) => {
      const step = item.node;
      const stepId = text(step.step_id, "");
      const label = shortLabel(text(step.title || step.step_id, String(index + 1)), 18);
      const stateClass = classForState(step.state);
      const selected = selectedStepId === stepId ? "selected" : "";
      const critical = criticalIds.has(stepId) ? "critical" : "";
      const ready = readyIds.has(stepId) ? "ready" : "";
      const blocked = blockedIds.has(stepId) ? "blocked" : "";
      return `<g class="plan-node ${escapeHtml(stateClass)} ${selected} ${critical} ${ready} ${blocked}" data-plan-id="${escapeHtml(text(plan.plan_id, ""))}" data-plan-step-id="${escapeHtml(stepId)}" role="button" tabindex="0">
        <circle cx="${item.x}" cy="${item.y}" r="13" />
        <text x="${item.x}" y="${item.y + 4}" text-anchor="middle">${escapeHtml(String(index + 1))}</text>
        <text class="plan-node-label" x="${item.x}" y="${item.y + 25}" text-anchor="middle">${escapeHtml(label)}</text>
      </g>`;
    })
    .join("");
  const dependencyCount = edges.length;
  const resultRefs = (Array.isArray(plan.steps) ? plan.steps : [])
    .map((step) => text(step.result_ref_id, ""))
    .filter(Boolean);
  const criticalLabel = criticalIds.size
    ? nodes
        .filter((node) => criticalIds.has(text(node.step_id, "")))
        .map((node) => shortLabel(text(node.title || node.step_id, ""), 18))
        .join(" -> ")
    : "-";
  return `<div class="plan-dag" aria-label="${escapeHtml(t("runtime.planGraph"))}">
    <div class="plan-dag-head">
      <span>${escapeHtml(t("runtime.planGraph"))}</span>
      <small>${escapeHtml(t("runtime.deps"))}: ${escapeHtml(text(dependencyCount, 0))}${resultRefs.length ? ` / ${escapeHtml(t("runtime.result"))}: ${escapeHtml(resultRefs.length)}` : ""}</small>
    </div>
    <svg viewBox="0 0 ${width} ${height}" role="img">
      <g>${edgeMarkup}</g>
      <g>${nodeMarkup}</g>
    </svg>
    <div class="plan-dag-hints">
      <small>${escapeHtml(t("runtime.critical"))}: ${escapeHtml(criticalLabel)}</small>
      <small>${escapeHtml(t("runtime.ready"))}: ${escapeHtml(text(readyIds.size, 0))} / ${escapeHtml(t("runtime.blocked"))}: ${escapeHtml(text(blockedIds.size, 0))}</small>
    </div>
  </div>`;
}

function renderRuntimePlanStepDetail(plan) {
  const selected = state.runtimeSelectedStep?.planId === text(plan.plan_id, "")
    ? resolveRuntimeSelectedStep([plan])
    : null;
  if (!selected) return "";
  const step = selected.step;
  const deps = Array.isArray(step.depends_on) ? step.depends_on.join(", ") : "";
  const rows = [
    [t("runtime.stepDetail"), text(step.title || step.step_id, "-")],
    [t("runtime.expectedTool"), text(step.expected_tool, "-")],
    [t("runtime.nanobotTask"), text(step.nanobot_task_id, "-")],
    [t("runtime.deps"), deps || "-"],
    [t("runtime.result"), text(step.result_ref_id || step.result_summary, "-")],
    [t("runtime.started"), formatTime(step.started_at)],
    [t("runtime.completed"), formatTime(step.completed_at)],
    [t("runtime.error"), text(step.error, "-")],
  ];
  return `<div class="plan-step-detail">
    ${rows.map(([label, value]) => `<div class="memory-kv-mini">
      <span>${escapeHtml(label)}</span>
      <strong title="${escapeHtml(text(value))}">${escapeHtml(text(value))}</strong>
    </div>`).join("")}
  </div>`;
}

function resolveRuntimeSelectedStep(plans) {
  const selected = state.runtimeSelectedStep;
  if (!selected) return null;
  for (const plan of plans) {
    if (text(plan.plan_id, "") !== selected.planId) continue;
    const step = (Array.isArray(plan.steps) ? plan.steps : []).find((item) => text(item.step_id, "") === selected.stepId);
    if (step) return { plan, step };
  }
  return null;
}

function bindRuntimePlanStepButtons() {
  document.querySelectorAll("[data-plan-step-id]").forEach((element) => {
    const select = () => {
      state.runtimeSelectedStep = {
        planId: element.dataset.planId || "",
        stepId: element.dataset.planStepId || "",
      };
      if (state.runtimeMonitor?.plans) renderRuntimePlans(state.runtimeMonitor.plans);
    };
    element.addEventListener("click", select);
    element.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
  });
}

function renderRuntimeNanobot(nanobot) {
  const status = nanobot.status || {};
  const refs = Array.isArray(nanobot.report_ref_ids) ? nanobot.report_ref_ids : [];
  $("runtimeNanobot").innerHTML = [
    runtimeMiniSection("state", text(status.state, "idle")),
    runtimeMiniSection(t("runtime.reports"), refs.length ? refs.join("\n") : "0"),
    runtimeMiniSection("stream", text(nanobot.dispatch_stream)),
    runtimeMiniSection("result", text(nanobot.result_channel)),
  ].join("");
}

function renderRuntimeAgentTeam(agentTeam, collaboration) {
  const members = Array.isArray(agentTeam.members) ? agentTeam.members : [];
  const flow = collaboration.goslo_to_nanobot || {};
  const chatroom = collaboration.chatroom || {};
  $("runtimeAgentTeam").innerHTML = [
    runtimeMiniSection("team", `${text(agentTeam.agent_team_id)} / ${text(agentTeam.status)}`),
    runtimeMiniSection("members", members.map((member) => `${text(member.role)}: ${text(member.worker)} (${text(member.state)})`).join("\n") || "-"),
    renderRuntimeChannelFlow(collaboration.channel_flow),
    runtimeMiniSection(t("runtime.collaboration"), Object.entries(flow).map(([k, v]) => `${k}: ${v}`).join("\n")),
    runtimeMiniSection(t("runtime.safeSurface"), text(chatroom.safe_surface, "-")),
  ].join("");
}

function renderRuntimeChannelFlow(flow) {
  const stages = Array.isArray(flow) ? flow : [];
  if (!stages.length) {
    return runtimeMiniSection(t("runtime.channelFlow"), "-");
  }
  return `<section class="runtime-flow" aria-label="${escapeHtml(t("runtime.channelFlow"))}">
    <div class="runtime-flow-head">
      <strong>${escapeHtml(t("runtime.channelFlow"))}</strong>
      <small>${escapeHtml(text(stages.length, 0))}</small>
    </div>
    <div class="runtime-flow-track">
      ${stages.map((stage, index) => `<article class="runtime-flow-node">
        <span class="status-light small ${escapeHtml(classForState(stage.status))}"></span>
        <strong title="${escapeHtml(text(stage.channel, ""))}">${escapeHtml(text(stage.label || stage.stage, "-"))}</strong>
        <small>${escapeHtml(text(stage.status, "idle"))} / ${escapeHtml(text(stage.detail, "-"))}</small>
        <code>${escapeHtml(text(stage.channel, "-"))}</code>
        ${index < stages.length - 1 ? `<span class="runtime-flow-arrow" aria-hidden="true">></span>` : ""}
      </article>`).join("")}
    </div>
  </section>`;
}

function runtimeMiniSection(label, body) {
  return `<article class="runtime-mini">
    <strong>${escapeHtml(label)}</strong>
    <small>${escapeHtml(text(body, "-"))}</small>
  </article>`;
}

async function loadMemoryPanel() {
  setLoading(true);
  try {
    const [response, poolResponse, activityResponse] = await Promise.all([
      fetch("/api/app/live-state?limit=80"),
      fetch("/api/l15/pool"),
      fetch("/api/memory/blackboard/activity?limit=12"),
    ]);
    const payload = await readJsonResponse(response, "/api/app/live-state?limit=80");
    const pool = await readJsonResponse(poolResponse, "/api/l15/pool");
    const activity = await readJsonResponse(activityResponse, "/api/memory/blackboard/activity?limit=12");
    state.memoryPrevious = state.memoryState;
    state.memoryDiff = diffMemoryState(state.memoryPrevious, payload);
    state.memoryDiffIds = state.memoryDiff.l2bNodes;
    renderMemoryState(payload);
    renderL15Pool(pool);
    renderMemoryBlackboardActivity(activity);
    $("lastFetch").textContent = t("last.fetched", {
      time: new Date().toLocaleTimeString(),
      ms: 0,
    });
  } finally {
    setLoading(false);
  }
}

function renderMemoryState(payload) {
  state.memoryState = payload;
  const blackboard = payload.blackboard || {};
  const intent = payload.intent_workspace || {};
  const refs = payload.refs || {};
  const l2b = payload.l2b || {};
  const tools = Array.isArray(payload.tool_artifacts) ? payload.tool_artifacts : [];
  const presentKeys = Number(blackboard.present_count || 0);
  const declaredKeys = Number(blackboard.declared_count || 0);
  const refCount = Number(refs.metrics?.total_refs || intent.ref_count || 0);
  const nodeCount = Number(l2b.node_count || 0);
  const edgeCount = Number(l2b.edge_count || 0);
  const sequence = Number(payload.sequence || 0);

  setLight("memoryLight", "good");
  setLight("memoryBlackboardLight", presentKeys > 0 ? "good" : "idle");
  setLight("memoryRefLight", refCount > 0 ? "good" : "idle");
  setLight("memoryL2bLight", nodeCount > 0 ? "good" : "idle");
  $("memoryTitle").textContent = `L2-B ${nodeCount} / ${edgeCount}`;
  $("memorySummary").textContent = [
    t("memory.readOnly"),
    t("memory.sequence", { count: sequence }),
    t("memory.generated", { time: formatTime(payload.generated_at) }),
  ].join(" / ");
  $("memoryBlackboardCount").textContent = `${presentKeys}/${declaredKeys}`;
  $("memoryRefCount").textContent = String(refCount);
  $("memoryNodeCount").textContent = `${nodeCount}/${edgeCount}`;
  setPill(
    "memoryGraphPill",
    nodeCount > 0 ? "good" : "",
    `${nodeCount} ${t("memory.nodes")} / ${edgeCount} ${t("memory.edges")}`,
  );
  setPill("memoryReadPill", "good", state.paused ? t("actions.pause") : "5s");
  setPill("memoryBlackboardPill", presentKeys > 0 ? "good" : "", `${presentKeys}/${declaredKeys}`);
  setPill("memoryIntentPill", (intent.ref_count || 0) > 0 ? "good" : "", String(intent.ref_count || 0));
  setPill("memoryToolPill", tools.length ? "good" : "", String(tools.length));
  renderMemoryLanes({ blackboard, intent, refs, l2b });
  renderMemoryBlackboard(blackboard);
  renderMemoryIntent(intent);
  renderMemoryGraph({ l2b, refs, intent, blackboard });
  renderMemoryTools(tools);
  renderMemoryDetail(payload);
  bindMemorySelectButtons();
}

function diffMemoryState(previous, next) {
  if (!previous) {
    return {
      l2bNodes: new Set(),
      blackboardKeys: new Set(),
      intentRefs: new Set(),
    };
  }
  return {
    l2bNodes: diffRowsById(previous?.l2b?.nodes, next?.l2b?.nodes, (row) => text(row.uuid, ""), l2bNodeSignature),
    blackboardKeys: diffRowsById(
      previous?.blackboard?.present_keys,
      next?.blackboard?.present_keys,
      (row) => text(row.key, ""),
      blackboardKeySignature,
    ),
    intentRefs: diffRowsById(
      previous?.intent_workspace?.refs,
      next?.intent_workspace?.refs,
      (row) => text(row.ref_id, ""),
      intentRefSignature,
    ),
  };
}

function diffRowsById(previousRows, nextRows, idFn, signatureFn) {
  const before = new Map();
  (Array.isArray(previousRows) ? previousRows : []).forEach((row) => {
    const id = idFn(row);
    if (id) before.set(id, signatureFn(row));
  });
  const changed = new Set();
  (Array.isArray(nextRows) ? nextRows : []).forEach((row) => {
    const id = idFn(row);
    if (!id) return;
    const signature = signatureFn(row);
    if (!before.has(id) || before.get(id) !== signature) changed.add(id);
  });
  return changed;
}

function stableSignature(parts) {
  return JSON.stringify(parts.map((part) => text(part, "")));
}

function l2bNodeSignature(node) {
  return stableSignature([
    node.label,
    node.kind,
    node.source,
    node.bucket,
    node.attention,
    node.confirmation,
    node.active,
    node.updated_at,
  ]);
}

function blackboardKeySignature(row) {
  return stableSignature([
    row.scope,
    row.writer,
    row.type_hint,
    row.exists,
    row.summary,
    row.event_driven,
  ]);
}

function intentRefSignature(row) {
  return stableSignature([
    row.title,
    row.kind,
    row.role,
    row.owner_id,
    row.origin,
    row.expires_in_seconds,
    row.related_node_uuid,
    row.related_intent_event_id,
  ]);
}

function renderL15Pool(payload) {
  state.l15Pool = payload;
  const buckets = Array.isArray(payload?.buckets) ? payload.buckets : [];
  const health = payload?.health || {};
  const rows = buckets.slice(0, 8);
  renderL15BucketOptions(buckets);
  $("l15PoolList").innerHTML = rows.length
    ? rows
        .map((bucket) => {
          const frozen = bucket.frozen ? "frozen" : "open";
          const pressure = text(health.capacity_pressure, "ok");
          const kind = text(bucket.kind);
          return `<article class="compact-list-row passive l15-bucket-card">
            <strong>${escapeHtml(text(bucket.kind))}</strong>
            <small>${escapeHtml(text(bucket.node_count, 0))} ${escapeHtml(t("memory.nodes"))} / ${escapeHtml(frozen)} / ${escapeHtml(t("memory.pressure"))}: ${escapeHtml(pressure)}</small>
            <span class="bucket-card-actions" aria-label="${escapeHtml(t("memory.bucketQuickHint"))}">
              <button class="button mini" type="button" data-l15-bucket="${escapeHtml(kind)}" data-l15-op="freeze">${escapeHtml(t("memory.freeze"))}</button>
              <button class="button mini" type="button" data-l15-bucket="${escapeHtml(kind)}" data-l15-op="unfreeze">${escapeHtml(t("memory.unfreeze"))}</button>
              <button class="button mini" type="button" data-l15-bucket="${escapeHtml(kind)}" data-l15-op="clear">${escapeHtml(t("memory.clear"))}</button>
            </span>
          </article>`;
        })
        .join("")
    : `<span class="empty">${t("empty.noData")}</span>`;
  bindL15BucketQuickActions();
}

function renderL15BucketOptions(buckets) {
  const select = $("l15BucketKind");
  if (!select) return;
  const current = select.value || "main";
  const defaults = [
    "main",
    "obsidian_setting_daily",
    "obsidian_setting_roleplay",
    "google_calendar",
    "autonomous_curiosity",
    "roleplay_temp",
  ];
  const values = [
    ...new Set([
      ...buckets.map((bucket) => text(bucket.kind, "")).filter(Boolean),
      ...defaults,
    ]),
  ];
  select.innerHTML = values
    .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)
    .join("");
  select.value = values.includes(current) ? current : values[0] || "main";
}

function renderMemoryOpsReceipt(payload) {
  state.memoryOpsReceipt = payload;
  updateMemoryDraftPreview(payload);
  $("memoryOpsOutput").textContent = JSON.stringify(payload, null, 2);
  setPill("memoryOpsPill", payload?.success ? "good" : "bad", text(payload?.action, t("pills.test")));
  if (state.memoryState) renderMemoryState(state.memoryState);
}

function updateMemoryDraftPreview(payload) {
  if (!payload?.success) return;
  const action = text(payload.action, "");
  const data = payload.data || {};
  const receiptId = text(payload.receipt?.receipt_id, `draft_${Date.now()}`);
  if (action.startsWith("l2b.node")) {
    if (action === "l2b.node.delete" && data.node_uuid) {
      state.memoryDraftPreview.deleteIds.add(text(data.node_uuid));
      return;
    }
    const observation = data.observation || {};
    if (!observation.label) return;
    const targetId = text(observation.meta?.target_node_uuid, "");
    const uuid = targetId || `draft:${receiptId}`;
    const node = {
      uuid,
      label: observation.label,
      kind: observation.kind || "object",
      source: "web_draft",
      bucket: "preview",
      attention: 0.22,
      confirmation: "draft",
      description: observation.description || "",
      _preview: true,
    };
    state.memoryDraftPreview.nodes = [
      node,
      ...state.memoryDraftPreview.nodes.filter((item) => text(item.uuid) !== uuid),
    ].slice(0, 6);
    if (targetId) state.memoryDraftPreview.updateIds.add(targetId);
    return;
  }
  if (action.startsWith("l2b.edge") && data.from_uuid && data.to_uuid) {
    const edge = {
      source: text(data.from_uuid),
      target: text(data.to_uuid),
      kind: text(data.edge?.kind, "associated_with"),
      strength: Number(data.edge?.strength || 0.5),
      edge_source: "web_draft",
      _preview: true,
    };
    const signature = `${edge.source}->${edge.target}:${edge.kind}`;
    state.memoryDraftPreview.edges = [
      { ...edge, signature },
      ...state.memoryDraftPreview.edges.filter((item) => item.signature !== signature),
    ].slice(0, 8);
  }
}

function clearMemoryDraftPreview() {
  const previewIds = new Set((state.memoryDraftPreview.nodes || []).map((node) => text(node.uuid, "")));
  const clearedNodeCount = previewIds.size;
  const clearedEdgeCount = (state.memoryDraftPreview.edges || []).length;
  state.memoryDraftPreview = {
    nodes: [],
    edges: [],
    deleteIds: new Set(),
    updateIds: new Set(),
  };
  if (state.memorySelected?.type === "l2b" && isDraftPreviewId(state.memorySelected.id, previewIds)) {
    state.memorySelected = null;
  }
  ["l2bTargetUuid", "l2bDeleteUuid", "l2bEdgeFrom", "l2bEdgeTo"].forEach((id) => {
    const element = $(id);
    if (element && isDraftPreviewId(element.value, previewIds)) element.value = "";
  });
  state.memoryOpsReceipt = {
    success: true,
    action: "memory.preview.clear",
    dry_run: true,
    operator_mode: false,
    data: {
      cleared_nodes: clearedNodeCount,
      cleared_edges: clearedEdgeCount,
    },
  };
  if ($("memoryOpsOutput")) $("memoryOpsOutput").textContent = JSON.stringify(state.memoryOpsReceipt, null, 2);
  setPill("memoryOpsPill", "good", state.memoryOpsReceipt.action);
  if (state.memoryState) renderMemoryState(state.memoryState);
}

function isDraftPreviewId(value, previewIds = new Set()) {
  const id = text(value, "");
  return id.startsWith("draft:") || previewIds.has(id);
}

function readMemoryFilters() {
  state.memoryGraphMode = text($("memoryGraphMode").value, "all") || "all";
  state.memoryFilters = {
    kind: text($("memoryFilterKind").value, "").trim().toLowerCase(),
    source: text($("memoryFilterSource").value, "").trim().toLowerCase(),
    bucket: text($("memoryFilterBucket").value, "").trim().toLowerCase(),
    minAttention: Number($("memoryFilterAttention").value || 0),
  };
  return state.memoryFilters;
}

function filteredMemoryNodes(nodes) {
  const filters = state.memoryFilters || {};
  return nodes.filter((node) => {
    const kind = text(node.kind, "").toLowerCase();
    const source = text(node.source, "").toLowerCase();
    const bucket = text(node.bucket_id || node.bucket, "").toLowerCase();
    const attention = Number(node.attention || 0);
    if (filters.kind && kind !== filters.kind) return false;
    if (filters.source && !source.includes(filters.source)) return false;
    if (filters.bucket && !bucket.includes(filters.bucket)) return false;
    if (attention < Number(filters.minAttention || 0)) return false;
    return true;
  });
}

function graphModeMemoryNodes(nodes, edges, l2b) {
  const mode = state.memoryGraphMode || "all";
  if (mode === "selected") {
    const selectedId = state.memorySelected?.type === "l2b" ? text(state.memorySelected.id, "") : "";
    if (selectedId) {
      const neighborIds = new Set([selectedId]);
      edges.forEach((edge) => {
        const source = text(edge.source, "");
        const target = text(edge.target, "");
        if (source === selectedId && target) neighborIds.add(target);
        if (target === selectedId && source) neighborIds.add(source);
      });
      const neighborhood = nodes.filter((node) => neighborIds.has(text(node.uuid, "")));
      if (neighborhood.length) return neighborhood;
    }
    return topAttentionMemoryNodes(nodes, l2b, 12);
  }
  if (mode === "attention") {
    return topAttentionMemoryNodes(nodes, l2b, 12);
  }
  return nodes;
}

function topAttentionMemoryNodes(nodes, l2b, limit) {
  const nodeMap = new Map(nodes.map((node) => [text(node.uuid, ""), node]));
  const rankedIds = (Array.isArray(l2b.top_attention) ? l2b.top_attention : [])
    .map((item) => text(item.uuid, ""))
    .filter((id) => id && nodeMap.has(id));
  const sortedIds = [...nodes]
    .sort((left, right) => Number(right.attention || 0) - Number(left.attention || 0))
    .map((node) => text(node.uuid, ""))
    .filter(Boolean);
  return [...new Set([...rankedIds, ...sortedIds])]
    .slice(0, limit)
    .map((id) => nodeMap.get(id))
    .filter(Boolean);
}

function applyMemoryFilters() {
  readMemoryFilters();
  if (state.memoryState) renderMemoryState(state.memoryState);
}

function readJsonObjectField(elementId) {
  const raw = $(elementId).value.trim();
  if (!raw) return {};
  const parsed = JSON.parse(raw);
  if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error(`${elementId}: expected a JSON object`);
  }
  return parsed;
}

function l15BucketOpPayload() {
  return {
    op: $("l15BucketOp").value,
    kind: $("l15BucketKind").value,
    payload: readJsonObjectField("l15BucketPayload"),
    dry_run: true,
    operator_mode: false,
  };
}

function renderMemoryLocalError(action, error) {
  renderMemoryOpsReceipt({
    success: false,
    action,
    dry_run: true,
    operator_mode: false,
    message: errorMessage(error),
  });
}

async function draftL15BucketOp() {
  let payload;
  try {
    payload = l15BucketOpPayload();
  } catch (error) {
    renderMemoryLocalError("l15.bucket_op.draft", error);
    return;
  }
  const receipt = await postJson("/api/l15/bucket-op/draft", payload);
  renderMemoryOpsReceipt(receipt);
}

async function dryRunL15BucketOp() {
  let payload;
  try {
    payload = l15BucketOpPayload();
  } catch (error) {
    renderMemoryLocalError("l15.bucket_op.apply", error);
    return;
  }
  const receipt = await postJson("/api/l15/bucket-op", payload);
  renderMemoryOpsReceipt(receipt);
}

function bindL15BucketQuickActions() {
  document.querySelectorAll("[data-l15-bucket][data-l15-op]").forEach((button) => {
    button.addEventListener("click", () => {
      $("l15BucketKind").value = button.dataset.l15Bucket || "main";
      $("l15BucketOp").value = button.dataset.l15Op || "freeze";
      $("l15BucketPayload").value = "{}";
      draftL15BucketOp();
    });
  });
}

function obsidianNodePayload() {
  return {
    profile: $("obsidianProfile").value,
    label: $("obsidianLabel").value,
    kind: $("obsidianKind").value,
    obsidian_uuid: $("obsidianUuid").value,
    description: "Created from Web Console operator workbench.",
    tags: ["web_console", $("obsidianProfile").value],
  };
}

async function draftObsidianNode() {
  const payload = await postJson("/api/l15/obsidian-node/draft", {
    ...obsidianNodePayload(),
    dry_run: true,
  });
  renderMemoryOpsReceipt(payload);
}

async function dryRunObsidianNode() {
  const payload = await postJson("/api/l15/obsidian-node", {
    ...obsidianNodePayload(),
    dry_run: true,
    operator_mode: false,
  });
  renderMemoryOpsReceipt(payload);
}

function l2bNodePayload(options = {}) {
  const includeTarget = options.includeTarget !== false;
  const payload = {
    label: $("l2bLabel").value,
    kind: $("l2bKind").value,
    description: $("l2bDescription").value,
    confidence: 0.85,
    confirmation: "confirmed",
  };
  if (includeTarget) {
    payload.node_uuid = $("l2bTargetUuid").value.trim();
  }
  return payload;
}

async function draftL2bNode() {
  const payload = await postJson("/api/l2b/node/draft", {
    ...l2bNodePayload(),
    dry_run: true,
  });
  renderMemoryOpsReceipt(payload);
}

async function dryRunL2bNode() {
  const payload = await postJson("/api/l2b/node", {
    ...l2bNodePayload({ includeTarget: false }),
    dry_run: true,
    operator_mode: false,
  });
  renderMemoryOpsReceipt(payload);
}

async function dryRunUpdateL2bNode() {
  const target = $("l2bTargetUuid").value.trim();
  if (!target) {
    renderMemoryLocalError("l2b.node.apply", new Error("Target UUID is required for update dry-run"));
    return;
  }
  const payload = await postJson("/api/l2b/node", {
    ...l2bNodePayload(),
    dry_run: true,
    operator_mode: false,
  });
  renderMemoryOpsReceipt(payload);
}

async function dryRunDeleteL2bNode() {
  const payload = await postJson("/api/l2b/node/delete", {
    node_uuid: $("l2bDeleteUuid").value,
    dry_run: true,
    operator_mode: false,
  });
  renderMemoryOpsReceipt(payload);
}

async function draftL2bEdge() {
  const edge = l2bEdgePayload();
  if (!validateL2bEdgePayload(edge, "l2b.edge.draft")) return;
  const payload = await postJson("/api/l2b/edge/draft", {
    ...edge,
    dry_run: true,
  });
  renderMemoryOpsReceipt(payload);
}

async function dryRunL2bEdge() {
  const edge = l2bEdgePayload();
  if (!validateL2bEdgePayload(edge, "l2b.edge.apply")) return;
  const payload = await postJson("/api/l2b/edge", {
    ...edge,
    dry_run: true,
    operator_mode: false,
  });
  renderMemoryOpsReceipt(payload);
}

function l2bEdgePayload() {
  return {
    from_uuid: $("l2bEdgeFrom").value.trim(),
    to_uuid: $("l2bEdgeTo").value.trim(),
    kind: $("l2bEdgeKind").value,
  };
}

function validateL2bEdgePayload(edge, action) {
  if (edge.from_uuid && edge.to_uuid && edge.from_uuid === edge.to_uuid) {
    renderMemoryLocalError(action, new Error("From and To must be different"));
    return false;
  }
  return true;
}

function selectedL2bNode() {
  if (state.memorySelected?.type !== "l2b" || !state.memoryState) return null;
  const selectedId = state.memorySelected.id;
  const persisted = (state.memoryState.l2b?.nodes || []).find((node) => text(node.uuid, "") === selectedId);
  if (persisted) return persisted;
  return (state.memoryDraftPreview.nodes || []).find((node) => text(node.uuid, "") === selectedId) || null;
}

function syncSelectedL2bToForms(options = {}) {
  const node = selectedL2bNode();
  if (!node) return false;
  const uuid = text(node.uuid, "");
  if ($("l2bTargetUuid")) $("l2bTargetUuid").value = uuid;
  if ($("l2bDeleteUuid")) $("l2bDeleteUuid").value = uuid;
  if (options.fillEditable) {
    if ($("l2bLabel")) $("l2bLabel").value = text(node.label || node.uuid, "");
    if ($("l2bDescription")) $("l2bDescription").value = text(node.description || node.summary, $("l2bDescription").value);
    if ($("l2bKind")) {
      const kind = text(node.kind, "");
      const hasKind = Array.from($("l2bKind").options).some((option) => option.value === kind);
      if (hasKind) $("l2bKind").value = kind;
    }
  }
  return true;
}

function useSelectedMemoryNode() {
  if (!syncSelectedL2bToForms({ fillEditable: true })) {
    renderMemoryLocalError("memory.selection.use", new Error("Select a L2-B node first"));
  }
}

function setSelectedMemoryEdgeEndpoint(fieldId) {
  const node = selectedL2bNode();
  if (!node) {
    renderMemoryLocalError("memory.selection.edge", new Error("Select a L2-B node first"));
    return;
  }
  $(fieldId).value = text(node.uuid, "");
}

function renderMemoryLanes({ blackboard, intent, refs, l2b }) {
  const lanes = [
    {
      id: "blackboard",
      label: t("memory.blackboard"),
      count: `${text(blackboard.present_count, 0)}/${text(blackboard.declared_count, 0)}`,
      detail: t("memory.present", { count: blackboard.present_count || 0 }),
      light: (blackboard.present_count || 0) > 0 ? "good" : "idle",
    },
    {
      id: "intent",
      label: t("memory.intent"),
      count: text(intent.ref_count, 0),
      detail: text(intent.pressure?.pressure_level, "ok"),
      light: (intent.ref_count || 0) > 0 ? "good" : "idle",
    },
    {
      id: "refs",
      label: t("memory.refs"),
      count: text(refs.metrics?.total_refs, 0),
      detail: Object.keys(refs.counts_by_kind || {}).join(", ") || t("pills.empty"),
      light: (refs.metrics?.total_refs || 0) > 0 ? "good" : "idle",
    },
    {
      id: "l2b",
      label: t("memory.l2b"),
      count: `${text(l2b.node_count, 0)}/${text(l2b.edge_count, 0)}`,
      detail: Object.entries(l2b.counts_by_kind || {})
        .map(([kind, count]) => `${kind}:${count}`)
        .join(", ") || t("memory.noNodes"),
      light: (l2b.node_count || 0) > 0 ? "good" : "idle",
    },
  ];
  $("memoryLanes").innerHTML = lanes
    .map((lane) => `<article class="memory-lane ${escapeHtml(lane.id)}">
      <span class="status-light small ${escapeHtml(lane.light)}"></span>
      <strong>${escapeHtml(lane.label)}</strong>
      <b>${escapeHtml(lane.count)}</b>
      <small>${escapeHtml(lane.detail)}</small>
    </article>`)
    .join("");
}

function groupRows(rows, keyFn) {
  const map = new Map();
  rows.forEach((row) => {
    const key = text(keyFn(row), "unknown");
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  });
  return Array.from(map.entries()).map(([label, items]) => ({ label, rows: items }));
}

function renderMemoryBlackboard(blackboard) {
  const present = Array.isArray(blackboard.present_keys) ? blackboard.present_keys : [];
  const declared = Array.isArray(blackboard.keys) ? blackboard.keys : [];
  const rows = (present.length ? present : declared.filter((row) => row.event_driven)).slice(0, 18);
  if (!rows.length) {
    $("memoryBlackboardList").innerHTML = `<span class="empty">${t("memory.emptyKeys")}</span>`;
    return;
  }
  const groups = groupRows(rows, (row) => `${text(row.scope, "scope")} / ${text(row.writer, "writer")}`).slice(0, 8);
  $("memoryBlackboardList").innerHTML = groups
    .map((group) => `<section class="memory-group">
      <div class="memory-group-head">
        <strong>${escapeHtml(group.label)}</strong>
        <small>${escapeHtml(t("memory.grouped"))}: ${escapeHtml(text(group.rows.length, 0))}</small>
      </div>
      ${group.rows.slice(0, 6).map((row) => {
        const id = text(row.key);
        const active = isMemorySelected("blackboard", id) ? "active" : "";
        const exists = row.exists ? "" : "muted";
        const changed = state.memoryDiff?.blackboardKeys?.has(id) ? "changed" : "";
        const changedLabel = changed ? `<small>${escapeHtml(t("memory.changed"))}</small>` : "";
        const evented = row.event_driven ? `<small>${escapeHtml(t("memory.eventDriven"))}</small>` : "";
        return `<button type="button" class="memory-list-row blackboard-card ${active} ${exists} ${changed}" data-memory-select-type="blackboard" data-memory-select-id="${escapeHtml(id)}">
          <span class="status-light small ${row.exists ? "good" : "idle"}"></span>
          <strong title="${escapeHtml(id)}">${escapeHtml(id)}</strong>
          <span class="memory-row-meta">
            <small>${escapeHtml(t("memory.scope"))}: ${escapeHtml(text(row.scope))}</small>
            <small>${escapeHtml(t("memory.writer"))}: ${escapeHtml(text(row.writer))}</small>
            <small>${escapeHtml(text(row.type_hint, "value"))}</small>
            ${changedLabel}
            ${evented}
          </span>
          <small>${escapeHtml(text(row.summary, "not_set"))}</small>
        </button>`;
      }).join("")}
    </section>`)
    .join("");
}

function renderMemoryBlackboardActivity(payload) {
  state.blackboardActivity = payload;
  const rows = Array.isArray(payload?.data?.activities) ? payload.data.activities : [];
  setPill("memoryBlackboardActivityPill", rows.length ? "good" : "", String(rows.length || 0));
  $("memoryBlackboardActivity").innerHTML = rows.length
    ? rows.slice(0, 12).map((row) => `<article class="memory-activity-row">
      <strong title="${escapeHtml(text(row.key, ""))}">${escapeHtml(shortLabel(text(row.key, "key"), 32))}</strong>
      <span class="memory-row-meta">
        <small>${escapeHtml(text(row.activity_type, "-"))}</small>
        <small>${escapeHtml(t("memory.scope"))}: ${escapeHtml(text(row.scope, "-"))}</small>
        <small>${escapeHtml(text(row.client_name, "-"))}</small>
      </span>
      <small>${escapeHtml(text(row.previous_summary, "-"))} -> ${escapeHtml(text(row.current_summary, "-"))}</small>
    </article>`).join("")
    : `<span class="empty">${t("memory.noActivity")}</span>`;
}

function renderMemoryIntent(intent) {
  const rows = Array.isArray(intent.refs) ? intent.refs.slice(0, 18) : [];
  if (!rows.length) {
    $("memoryIntentList").innerHTML = `<span class="empty">${t("memory.emptyRefs")}</span>`;
    return;
  }
  const groups = groupRows(rows, (row) => {
    const role = text(row.role || row.kind, "ref");
    const owner = text(row.owner_id, "parent");
    return `${role} / ${owner}`;
  }).slice(0, 8);
  $("memoryIntentList").innerHTML = groups
    .map((group) => `<section class="memory-group">
      <div class="memory-group-head">
        <strong>${escapeHtml(group.label)}</strong>
        <small>${escapeHtml(t("memory.grouped"))}: ${escapeHtml(text(group.rows.length, 0))}</small>
      </div>
      ${group.rows.slice(0, 6).map((row) => {
        const id = text(row.ref_id);
        const title = text(row.title || row.ref_id, row.kind || "ref");
        const active = isMemorySelected("intent", id) ? "active" : "";
        const changed = state.memoryDiff?.intentRefs?.has(id) ? "changed" : "";
        const changedLabel = changed ? `<small>${escapeHtml(t("memory.changed"))}</small>` : "";
        const linked = row.related_node_uuid || row.related_intent_event_id ? `<small>${escapeHtml(t("memory.linked"))}</small>` : "";
        return `<button type="button" class="memory-list-row intent-card ${active} ${changed}" data-memory-select-type="intent" data-memory-select-id="${escapeHtml(id)}">
          <span class="status-light small ${linked ? "good" : "idle"}"></span>
          <strong title="${escapeHtml(title)}">${escapeHtml(title)}</strong>
          <span class="memory-row-meta">
            <small>${escapeHtml(text(row.kind, "ref"))}</small>
            <small>${escapeHtml(t("memory.owner"))}: ${escapeHtml(text(row.owner_id, "parent"))}</small>
            <small>${escapeHtml(t("memory.expires"))}: ${escapeHtml(formatExpires(row.expires_in_seconds))}</small>
            ${changedLabel}
            ${linked}
          </span>
          <small>${escapeHtml(id)}</small>
        </button>`;
      }).join("")}
    </section>`)
    .join("");
}

function renderMemoryGraph({ l2b, refs, intent, blackboard }) {
  const baseNodes = Array.isArray(l2b.nodes) ? l2b.nodes : [];
  const baseIds = new Set(baseNodes.map((node) => text(node.uuid, "")));
  const preview = state.memoryDraftPreview || {};
  const previewNodes = (Array.isArray(preview.nodes) ? preview.nodes : [])
    .filter((node) => !baseIds.has(text(node.uuid, "")));
  const edges = [
    ...(Array.isArray(l2b.edges) ? l2b.edges : []),
    ...(Array.isArray(preview.edges) ? preview.edges : []),
  ];
  const filteredNodes = filteredMemoryNodes([...baseNodes, ...previewNodes]);
  const nodes = graphModeMemoryNodes(filteredNodes, edges, l2b);
  if (!nodes.length) {
    renderMemoryGraphPlaceholder({ refs, intent, blackboard });
    return;
  }
  const graphNodes = nodes.slice(0, 32);
  const hiddenCount = Math.max(0, filteredNodes.length - graphNodes.length);
  const positions = memoryGraphLayout(graphNodes);
  const positionMap = new Map(positions.map((item) => [item.id, item]));
  const selectedId = state.memorySelected?.type === "l2b" ? state.memorySelected.id : "";
  const selectedNode = selectedId ? graphNodes.find((node) => text(node.uuid, "") === selectedId) : null;
  setPill(
    "memoryCanvasSelectionPill",
    selectedNode ? "good" : "",
    selectedNode ? shortLabel(text(selectedNode.label || selectedNode.uuid, selectedId), 24) : t("metrics.selection"),
  );
  const topIds = new Set((Array.isArray(l2b.top_attention) ? l2b.top_attention : [])
    .slice(0, 4)
    .map((item) => text(item.uuid, "")));
  const visibleEdges = edges
    .filter((edge) => positionMap.has(text(edge.source, "")) && positionMap.has(text(edge.target, "")))
    .slice(0, 80);
  const edgeMarkup = visibleEdges
    .map((edge) => {
      const source = positionMap.get(text(edge.source, ""));
      const target = positionMap.get(text(edge.target, ""));
      const strength = Math.max(0.18, Math.min(1, Number(edge.strength || 0.35)));
      const cross = edge.cross_compartment ? "cross" : "";
      const selected = selectedId && (text(edge.source, "") === selectedId || text(edge.target, "") === selectedId) ? "selected" : "";
      const previewEdge = edge._preview ? "preview" : "";
      const title = `${text(edge.kind, "edge")} / ${text(edge.edge_source || edge.source_kind || edge.source, "")}`;
      return `<line class="memory-edge ${cross} ${selected} ${previewEdge}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" style="opacity:${strength.toFixed(2)}">
        <title>${escapeHtml(title)}</title>
      </line>`;
    })
    .join("");
  const edgeHintMarkup = visibleEdges
    .map((edge, index) => {
      const source = positionMap.get(text(edge.source, ""));
      const target = positionMap.get(text(edge.target, ""));
      return memoryEdgeHintMarkup(edge, source, target, selectedId, index, graphNodes.length);
    })
    .filter(Boolean)
    .join("");
  const externalLinks = memoryExternalLinks({ refs, intent, positionMap });
  const linkMarkup = externalLinks
    .map((link) => {
      const target = positionMap.get(link.targetId);
      const bend = link.x < target.x ? 82 : -82;
      return `<path class="memory-ref-link ${escapeHtml(link.kind)}" d="M${link.x} ${link.y} C${link.x + bend} ${link.y}, ${target.x - bend} ${target.y}, ${target.x} ${target.y}" />`;
    })
    .join("");
  const linkNodeMarkup = externalLinks
    .map((link) => `<g class="memory-ref-node ${escapeHtml(link.kind)}" data-memory-select-type="${escapeHtml(link.selectType)}" data-memory-select-id="${escapeHtml(link.id)}" role="button" tabindex="0">
      <circle cx="${link.x}" cy="${link.y}" r="8" />
      <text x="${link.x}" y="${link.y - 13}" text-anchor="middle">${escapeHtml(shortLabel(link.label, 15))}</text>
    </g>`)
    .join("");
  const showLabels = graphNodes.length <= 18;
  const nodeMarkup = positions
    .map((item) => {
      const node = item.node;
      const id = text(node.uuid);
      const label = shortLabel(text(node.label || node.uuid, "node"), 24);
      const tone = memoryNodeTone(node);
      const selected = selectedId === id ? "selected" : "";
      const changed = state.memoryDiffIds?.has(id) ? "changed" : "";
      const previewNode = node._preview || state.memoryDraftPreview.updateIds?.has(id) ? "preview" : "";
      const deletePreview = state.memoryDraftPreview.deleteIds?.has(id) ? "delete-preview" : "";
      const labelMarkup = showLabels || selected || topIds.has(id)
        ? `<text x="${item.x}" y="${item.y + item.r + 17}" text-anchor="middle">${escapeHtml(label)}</text>`
        : "";
      const changeLabel = changed ? `<text class="memory-node-change" x="${item.x}" y="${item.y - item.r - 8}" text-anchor="middle">${escapeHtml(t("memory.changed"))}</text>` : "";
      return `<g class="memory-svg-node ${tone} ${selected} ${changed} ${previewNode} ${deletePreview}" data-memory-select-type="l2b" data-memory-select-id="${escapeHtml(id)}" role="button" tabindex="0">
        <title>${escapeHtml(text(node.label || node.uuid))}</title>
        <circle cx="${item.x}" cy="${item.y}" r="${item.r}" />
        <text class="memory-node-glyph" x="${item.x}" y="${item.y + 4}" text-anchor="middle">${escapeHtml(memoryKindGlyph(node.kind))}</text>
        ${changeLabel}
        ${labelMarkup}
      </g>`;
    })
    .join("");
  const graphNotes = [
    t(state.memoryGraphMode === "selected"
      ? "memory.graphModeSelected"
      : state.memoryGraphMode === "attention"
        ? "memory.graphModeAttention"
        : "memory.graphModeAll"),
    `${graphNodes.length} ${t("memory.visible")}`,
    hiddenCount ? t("memory.hidden", { count: hiddenCount }) : "",
    externalLinks.length ? `${t("memory.refLinks")}: ${text(externalLinks.length, 0)}` : "",
  ].filter(Boolean).join(" / ");
  setPill("memoryGraphPill", graphNodes.length > 0 ? "good" : "", `${graphNodes.length}/${filteredNodes.length} ${t("memory.visible")}`);
  $("memoryGraph").innerHTML = `<div class="memory-graph-canvas">
    <svg class="memory-graph-svg" viewBox="0 0 960 520" role="img" aria-label="${escapeHtml(t("memory.graphMap"))}">
      <g class="memory-edges">${edgeMarkup}${linkMarkup}</g>
      <g class="memory-edge-hints">${edgeHintMarkup}</g>
      <g class="memory-ref-nodes">${linkNodeMarkup}</g>
      <g class="memory-nodes">${nodeMarkup}</g>
    </svg>
    <span class="memory-graph-note">${escapeHtml(graphNotes)}</span>
  </div>`;
}

function memoryEdgeHintMarkup(edge, source, target, selectedId, index, nodeCount) {
  const sourceId = text(edge.source, "");
  const targetId = text(edge.target, "");
  const selected = selectedId && (sourceId === selectedId || targetId === selectedId);
  const cross = Boolean(edge.cross_compartment);
  if (!cross && !selected && (nodeCount > 14 || index >= 18)) return "";
  const kind = shortLabel(text(edge.kind, "edge"), cross ? 15 : 18);
  const label = cross ? `${t("memory.crossCompartment")}: ${kind}` : kind;
  const midX = (source.x + target.x) / 2;
  const midY = (source.y + target.y) / 2;
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const length = Math.max(1, Math.sqrt(dx * dx + dy * dy));
  const offsetX = (-dy / length) * 12;
  const offsetY = (dx / length) * 12;
  const x = Math.round(midX + offsetX);
  const y = Math.round(midY + offsetY);
  const width = Math.min(150, Math.max(36, label.length * 6 + 14));
  const classes = [cross ? "cross" : "", selected ? "selected" : ""].filter(Boolean).join(" ");
  return `<g class="memory-edge-hint ${classes}">
    <rect x="${Math.round(x - width / 2)}" y="${Math.round(y - 9)}" width="${width}" height="18" rx="6" />
    <text x="${x}" y="${y + 4}" text-anchor="middle">${escapeHtml(label)}</text>
  </g>`;
}

function memoryExternalLinks({ refs, intent, positionMap }) {
  const links = [];
  const intentRefs = Array.isArray(intent.refs) ? intent.refs : [];
  intentRefs.forEach((row) => {
    const targetId = text(row.related_node_uuid, "");
    if (!targetId || !positionMap.has(targetId)) return;
    links.push({
      kind: "intent",
      selectType: "intent",
      id: text(row.ref_id),
      label: text(row.title || row.ref_id, "intent"),
      targetId,
    });
  });
  const resolvedRefs = Array.isArray(refs.resolved_l2b_targets) ? refs.resolved_l2b_targets : [];
  resolvedRefs.forEach((row) => {
    const targetId = text(row.target_id, "");
    if (!targetId || !positionMap.has(targetId)) return;
    links.push({
      kind: "ref",
      selectType: "ref",
      id: text(row.ref_id),
      label: text(row.kind || row.ref_id, "ref"),
      targetId,
    });
  });
  return links.slice(0, 24).map((link, index) => ({
    ...link,
    x: index % 2 === 0 ? 68 : 892,
    y: 44 + (index % 9) * 48 + Math.floor(index / 18) * 14,
  }));
}

function renderMemoryGraphPlaceholder({ refs, intent, blackboard }) {
  setPill("memoryCanvasSelectionPill", "", t("metrics.selection"));
  const buckets = Array.isArray(state.l15Pool?.buckets) ? state.l15Pool.buckets : [];
  const openBuckets = buckets.filter((bucket) => !bucket.frozen).length;
  const cards = [
    {
      id: "blackboard",
      label: t("memory.blackboard"),
      count: `${text(blackboard.present_count, 0)}/${text(blackboard.declared_count, 0)}`,
      detail: t("memory.present", { count: blackboard.present_count || 0 }),
      light: (blackboard.present_count || 0) > 0 ? "good" : "idle",
    },
    {
      id: "intent",
      label: t("memory.intent"),
      count: text(intent.ref_count, 0),
      detail: text(intent.pressure?.pressure_level, "ok"),
      light: (intent.ref_count || 0) > 0 ? "good" : "idle",
    },
    {
      id: "refs",
      label: t("memory.refs"),
      count: text(refs.metrics?.total_refs, 0),
      detail: Object.keys(refs.counts_by_kind || {}).join(", ") || t("pills.empty"),
      light: (refs.metrics?.total_refs || 0) > 0 ? "good" : "idle",
    },
    {
      id: "l15",
      label: "L1.5",
      count: text(buckets.length, 0),
      detail: `${openBuckets} ${t("memory.open")} / ${t("memory.buckets")}`,
      light: buckets.length ? "good" : "idle",
    },
    {
      id: "l2b",
      label: t("memory.l2b"),
      count: "0/0",
      detail: t("memory.waitingForNodes"),
      light: "idle",
    },
  ];
  const points = [
    { id: "blackboard", label: t("memory.blackboard"), x: 190, y: 150, count: blackboard.declared_count || 0 },
    { id: "intent", label: t("memory.intent"), x: 480, y: 110, count: intent.ref_count || 0 },
    { id: "refs", label: t("memory.refs"), x: 770, y: 150, count: refs.metrics?.total_refs || 0 },
    { id: "l2b", label: t("memory.l2b"), x: 480, y: 360, count: 0 },
  ];
  $("memoryGraph").innerHTML = `<div class="memory-graph-canvas placeholder dsg-placeholder">
    <div class="dsg-compartment-map" aria-label="${escapeHtml(t("memory.dsgState"))}">
      <div class="dsg-map-title">
        <strong>${escapeHtml(t("memory.dsgState"))}</strong>
        <small>${escapeHtml(t("memory.waitingForNodes"))}</small>
      </div>
      <div class="dsg-compartment-grid">
        ${cards.map((card) => `<article class="dsg-compartment-card ${escapeHtml(card.id)}">
          <span class="status-light small ${escapeHtml(card.light)}"></span>
          <strong>${escapeHtml(card.label)}</strong>
          <b>${escapeHtml(card.count)}</b>
          <small>${escapeHtml(card.detail)}</small>
        </article>`).join("")}
      </div>
    </div>
    <svg class="memory-graph-svg" viewBox="0 0 960 520" role="img" aria-label="${escapeHtml(t("memory.graphPlaceholder"))}">
      <path class="memory-edge placeholder" d="M190 150 C310 70 370 80 480 110" />
      <path class="memory-edge placeholder" d="M770 150 C650 70 590 80 480 110" />
      <path class="memory-edge placeholder" d="M480 110 C440 210 440 285 480 360" />
      ${points.map((point) => `<g class="memory-svg-node idle">
        <circle cx="${point.x}" cy="${point.y}" r="22" />
        <text class="memory-node-glyph" x="${point.x}" y="${point.y + 4}" text-anchor="middle">${escapeHtml(memoryKindGlyph(point.id))}</text>
        <text x="${point.x}" y="${point.y + 42}" text-anchor="middle">${escapeHtml(point.label)}</text>
        <text class="memory-node-count" x="${point.x}" y="${point.y + 58}" text-anchor="middle">${escapeHtml(text(point.count, 0))}</text>
      </g>`).join("")}
    </svg>
    <span class="empty">${escapeHtml(t("memory.graphPlaceholder"))}</span>
  </div>`;
}

function memoryGraphLayout(nodes) {
  const width = 960;
  const height = 520;
  const cx = width / 2;
  const cy = height / 2;
  if (nodes.length === 1) {
    const node = nodes[0];
    return [{ id: text(node.uuid), node, x: cx, y: cy, r: memoryNodeRadius(node) }];
  }
  const radiusX = nodes.length > 18 ? 390 : 340;
  const radiusY = nodes.length > 18 ? 190 : 160;
  return nodes.map((node, index) => {
    const angle = (-Math.PI / 2) + (index / nodes.length) * Math.PI * 2;
    const attention = Math.max(0, Math.min(1, Number(node.attention || 0)));
    const sourceShift = text(node.source, "").length % 3;
    return {
      id: text(node.uuid),
      node,
      x: Math.round(cx + Math.cos(angle) * (radiusX - sourceShift * 18)),
      y: Math.round(cy + Math.sin(angle) * (radiusY + attention * 20)),
      r: memoryNodeRadius(node),
    };
  });
}

function memoryNodeRadius(node) {
  return Math.round(13 + Math.max(0, Math.min(1, Number(node.attention || 0))) * 9);
}

function memoryNodeTone(node) {
  if (Number(node.attention || 0) > 0) return "good";
  if (text(node.confirmation, "").toLowerCase().includes("candidate")) return "warn";
  return "idle";
}

function memoryKindGlyph(kind) {
  const value = text(kind, "n").toLowerCase();
  if (value.includes("photo")) return "P";
  if (value.includes("event") || value.includes("episode")) return "E";
  if (value.includes("semantic") || value.includes("entity")) return "S";
  if (value.includes("ref")) return "R";
  if (value.includes("blackboard")) return "B";
  if (value.includes("intent")) return "I";
  if (value.includes("l2b")) return "L";
  return value.slice(0, 1).toUpperCase() || "N";
}

function renderMemoryDetail(payload) {
  const selected = resolveMemorySelection(payload);
  if (!selected) {
    renderDefaultMemoryDetail(payload);
    return;
  }
  if (selected.type === "l2b") {
    const l2b = payload.l2b || {};
    const edges = [
      ...(Array.isArray(l2b.edges) ? l2b.edges : []),
      ...(Array.isArray(state.memoryDraftPreview.edges) ? state.memoryDraftPreview.edges : []),
    ];
    const edgeCount = edges.filter((edge) =>
      text(edge.source, "") === selected.id || text(edge.target, "") === selected.id,
    ).length;
    const subtitle = selected.item._preview
      ? `${t("memory.l2b")} / ${t("memory.preview")}`
      : t("memory.l2b");
    renderMemoryDetailCard(
      text(selected.item.label || selected.item.uuid, "node"),
      subtitle,
      [
        [t("memory.kind"), selected.item.kind],
        [t("memory.attention"), selected.item.attention],
        [t("memory.confirmation"), selected.item.confirmation],
        [t("memory.source"), selected.item.source],
        [t("memory.connections"), edgeCount],
        [t("memory.preview"), selected.item._preview ? "true" : "false"],
        ["uuid", selected.item.uuid],
      ],
    );
    return;
  }
  if (selected.type === "blackboard") {
    renderMemoryDetailCard(
      text(selected.item.key, "key"),
      t("memory.blackboard"),
      [
        [t("memory.scope"), selected.item.scope],
        [t("memory.writer"), selected.item.writer],
        ["type", selected.item.type_hint],
        ["event", selected.item.event_driven ? "true" : "false"],
        ["summary", selected.item.summary],
        ["value", selected.item.value],
      ],
    );
    return;
  }
  if (selected.type === "ref") {
    renderMemoryDetailCard(
      text(selected.item.ref_id, "ref"),
      t("memory.refs"),
      [
        ["ref_id", selected.item.ref_id],
        [t("memory.kind"), selected.item.kind],
        ["target", `${text(selected.item.target_kind, "-")}:${text(selected.item.target_id, "-")}`],
        [t("memory.source"), selected.item.source || "-"],
      ],
    );
    return;
  }
  renderMemoryDetailCard(
    text(selected.item.title || selected.item.ref_id, "ref"),
    t("memory.intent"),
    [
      ["ref_id", selected.item.ref_id],
      [t("memory.kind"), selected.item.kind],
      [t("memory.owner"), selected.item.owner_id || "parent"],
      ["role", selected.item.role],
      [t("memory.expires"), formatExpires(selected.item.expires_in_seconds)],
      [t("memory.linked"), selected.item.related_node_uuid || selected.item.related_intent_event_id || "-"],
    ],
  );
}

function renderDefaultMemoryDetail(payload) {
  const l2b = payload.l2b || {};
  const top = Array.isArray(l2b.top_attention) ? l2b.top_attention : [];
  const audit = payload.audit || {};
  setPill("memoryDetailPill", "", t("memory.liveSnapshot"));
  $("memoryDetail").innerHTML = `<div class="memory-detail-head">
    <strong>${escapeHtml(t("memory.noSelection"))}</strong>
    <small>${escapeHtml(t("memory.topAttention"))}</small>
  </div>
  <div class="memory-top-list">
    ${top.length ? top.map((item) => `<button type="button" class="memory-top-item" data-memory-select-type="l2b" data-memory-select-id="${escapeHtml(text(item.uuid))}">
      <strong title="${escapeHtml(text(item.label || item.uuid))}">${escapeHtml(shortLabel(text(item.label || item.uuid), 38))}</strong>
      <small>${escapeHtml(text(item.kind, "node"))} / ${escapeHtml(text(item.attention, 0))}</small>
    </button>`).join("") : `<span class="empty">${escapeHtml(t("memory.noNodes"))}</span>`}
  </div>
  <div class="memory-detail-grid">
    ${memoryDetailKv(t("memory.readOnly"), audit.read_only ? "true" : "false")}
    ${memoryDetailKv(t("memory.edgeCount", { count: Number(l2b.edge_count || 0) }), `${Number(l2b.node_count || 0)} ${t("memory.nodes")}`)}
  </div>`;
}

function renderMemoryDetailCard(title, subtitle, rows) {
  setPill("memoryDetailPill", "good", subtitle);
  $("memoryDetail").innerHTML = `<div class="memory-detail-head">
    <strong title="${escapeHtml(title)}">${escapeHtml(title)}</strong>
    <small>${escapeHtml(subtitle)}</small>
  </div>
  <div class="memory-detail-grid">
    ${rows.map(([label, value]) => memoryDetailKv(label, value)).join("")}
  </div>`;
}

function memoryDetailKv(label, value) {
  return `<div class="memory-kv-mini">
    <span>${escapeHtml(text(label))}</span>
    <strong title="${escapeHtml(text(value))}">${escapeHtml(text(value))}</strong>
  </div>`;
}

function resolveMemorySelection(payload) {
  const selected = state.memorySelected;
  if (!selected) return null;
  if (selected.type === "l2b") {
    const item = [
      ...(payload.l2b?.nodes || []),
      ...(state.memoryDraftPreview.nodes || []),
    ].find((node) => text(node.uuid, "") === selected.id);
    return item ? { ...selected, item } : null;
  }
  if (selected.type === "blackboard") {
    const item = (payload.blackboard?.keys || []).find((row) => text(row.key, "") === selected.id);
    return item ? { ...selected, item } : null;
  }
  if (selected.type === "intent") {
    const item = (payload.intent_workspace?.refs || []).find((row) => text(row.ref_id, "") === selected.id);
    return item ? { ...selected, item } : null;
  }
  if (selected.type === "ref") {
    const item = (payload.refs?.refs || []).find((row) => text(row.ref_id, "") === selected.id);
    return item ? { ...selected, item } : null;
  }
  return null;
}

function bindMemorySelectButtons() {
  document.querySelectorAll("[data-memory-select-type]").forEach((element) => {
    const select = () => {
      state.memorySelected = {
        type: element.dataset.memorySelectType,
        id: element.dataset.memorySelectId,
      };
      syncSelectedL2bToForms();
      if (state.memoryState) renderMemoryState(state.memoryState);
    };
    element.addEventListener("click", select);
    element.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        select();
      }
    });
  });
}

function isMemorySelected(type, id) {
  return state.memorySelected?.type === type && state.memorySelected?.id === id;
}

function shortLabel(value, limit = 22) {
  const label = text(value, "");
  if (label.length <= limit) return label;
  return `${label.slice(0, Math.max(1, limit - 1))}...`;
}

function formatExpires(seconds) {
  if (seconds === null || seconds === undefined || seconds === "") return "-";
  const value = Number(seconds);
  if (!Number.isFinite(value)) return text(seconds);
  if (value < 0) return "expired";
  if (value < 60) return `${Math.round(value)}s`;
  if (value < 3600) return `${Math.round(value / 60)}m`;
  return `${Math.round(value / 3600)}h`;
}

function renderMemoryTools(tools) {
  if (!tools.length) {
    $("memoryTools").innerHTML = `<span class="empty">${t("memory.noArtifacts")}</span>`;
    return;
  }
  $("memoryTools").innerHTML = tools
    .map((tool) => {
      const locations = tool.locations || {};
      const activePlaces = ["blackboard", "intent_workspace", "ref_registry", "l2b"]
        .filter((name) => locations[name]?.present)
        .length;
      const light = activePlaces > 0 || tool.status === "active" ? "good" : classForState(tool.status);
      return `<article class="memory-tool">
        <span class="status-light small ${escapeHtml(light)}"></span>
        <strong title="${escapeHtml(text(tool.label || tool.tool_id))}">${escapeHtml(text(tool.label || tool.tool_id))}</strong>
        <small>${escapeHtml(text(tool.status))} / ${activePlaces}</small>
      </article>`;
    })
    .join("");
}

async function loadGraphitiPanel() {
  setLoading(true);
  try {
    const response = await fetch("/api/graphiti/status");
    const payload = await readJsonResponse(response, "/api/graphiti/status");
    renderGraphitiStatus(payload);
    if (!state.graphitiSearch) renderGraphitiSearch(null);
    if (!state.graphitiDraft) renderGraphitiDraft(null);
    $("lastFetch").textContent = t("last.fetched", {
      time: new Date().toLocaleTimeString(),
      ms: 0,
    });
  } finally {
    setLoading(false);
  }
}

function renderGraphitiStatus(payload) {
  state.graphitiStatus = payload;
  const data = payload?.data || {};
  const partitions = Array.isArray(data.partitions) ? data.partitions : [];
  const available = Boolean(payload?.available);
  const statusClass = available ? "good" : "warn";

  setLight("graphitiLight", statusClass);
  $("graphitiTitle").textContent = available ? t("graphiti.available") : t("graphiti.unavailable");
  $("graphitiSummary").textContent = text(payload?.message, t("empty.noData"));
  $("graphitiPartitionCount").textContent = String(partitions.length);
  $("graphitiConfigState").textContent = data.falkordb
    ? `${text(data.falkordb.host)}:${text(data.falkordb.port)}/${text(data.falkordb.database)}`
    : text(data.config_error, t("empty.noData"));
  setPill(
    "graphitiStatusPill",
    statusClass,
    available ? t("graphiti.available") : t("graphiti.unavailable"),
  );
  renderGraphitiPartitions(partitions);
  renderGraphitiPartitionSelect(partitions);
}

function renderGraphitiPartitions(partitions) {
  const list = $("graphitiPartitions");
  if (!partitions.length) {
    list.innerHTML = `<span class="empty">${t("graphiti.noPartitions")}</span>`;
    return;
  }
  list.innerHTML = partitions
    .map((partition) => `<span class="partition-chip">${escapeHtml(text(partition))}</span>`)
    .join("");
}

function renderGraphitiPartitionSelect(partitions) {
  const select = $("graphitiSearchPartition");
  const current = select.value || "goslo";
  const values = partitions.length ? partitions : ["goslo", "maid", "scene", "user"];
  select.innerHTML = values
    .map((partition) => `<option value="${escapeHtml(partition)}">${escapeHtml(partition)}</option>`)
    .join("");
  select.value = values.includes(current) ? current : values[0];
}

async function searchGraphiti() {
  const payload = await postJson("/api/graphiti/search", {
    query: $("graphitiSearchQuery").value,
    partition: $("graphitiSearchPartition").value,
    limit: $("graphitiSearchLimit").value,
  });
  renderGraphitiSearch(payload);
}

function renderGraphitiSearch(payload) {
  state.graphitiSearch = payload;
  const rows = Array.isArray(payload?.data?.results) ? payload.data.results : [];
  const unavailable = payload?.available === false;
  const label = unavailable
    ? t("graphiti.unavailable")
    : text(payload?.message, t("graphiti.results"));
  $("graphitiResultCount").textContent = String(rows.length);
  setPill(
    "graphitiSearchPill",
    !payload ? "" : payload.success ? "good" : "warn",
    !payload ? t("pills.empty") : label,
  );
  if (!payload) {
    $("graphitiResults").innerHTML = `<span class="empty">${t("graphiti.noResults")}</span>`;
    return;
  }
  if (!rows.length) {
    $("graphitiResults").innerHTML = `<span class="empty">${escapeHtml(unavailable ? t("graphiti.unavailable") : text(payload.message, t("graphiti.noResults")))}</span>`;
    return;
  }
  $("graphitiResults").innerHTML = rows
    .map((row) => `<article class="graphiti-result">
      <span class="status-light small good"></span>
      <strong title="${escapeHtml(text(row.uuid || row.source_node_uuid || row.target_node_uuid))}">
        ${escapeHtml(text(row.uuid || row.source_node_uuid || row.target_node_uuid, "fact"))}
      </strong>
      <small>${escapeHtml(text(row.score, "score -"))}</small>
      <p>${escapeHtml(text(row.text))}</p>
    </article>`)
    .join("");
}

async function draftGraphitiEpisode(useDryRun = false) {
  const payload = await postJson(
    useDryRun ? "/api/graphiti/episode" : "/api/graphiti/episode/draft",
    {
      name: $("graphitiEpisodeName").value,
      body: $("graphitiEpisodeBody").value,
      partition: $("graphitiSearchPartition").value,
      dry_run: true,
      source_description: "app-web-console",
    },
  );
  renderGraphitiDraft(payload);
}

function renderGraphitiDraft(payload) {
  state.graphitiDraft = payload;
  setPill(
    "graphitiDraftPill",
    !payload ? "" : payload.success ? "good" : "warn",
    !payload ? t("pills.empty") : text(payload.message, t("graphiti.draft")),
  );
  $("graphitiDraftOutput").textContent = payload
    ? JSON.stringify(payload, null, 2)
    : t("graphiti.operatorNote");
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return readJsonResponse(response, url);
}

function renderActiveViewError(error) {
  const message = errorMessage(error);
  $("lastFetch").textContent = t("errors.loadFailed", { message });

  if (state.activeView === "lineb") {
    setLight("voiceRouteLight", "bad");
    renderLinebResult({ status: "error", message });
  } else if (state.activeView === "runtime") {
    setLight("runtimeLight", "bad");
    renderTriggerReceipt({ success: false, action: "load", message });
  } else if (state.activeView === "canvas") {
    setLight("canvasLight", "bad");
    $("canvasSummary").textContent = message;
  } else if (state.activeView === "memory") {
    setLight("memoryLight", "bad");
    renderMemoryOpsReceipt({ success: false, action: "load", message });
  } else if (state.activeView === "graphiti") {
    renderGraphitiStatus({
      available: false,
      success: false,
      message,
      data: { partitions: [] },
    });
    renderGraphitiSearch({ available: false, success: false, message, data: { results: [] } });
    renderGraphitiDraft({ success: false, action: "load", message });
  } else {
    renderEnvelope({
      ok: false,
      state: "error",
      upstream: {},
      detail: { message },
      summary: {},
      status: null,
    });
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function activateView(viewName) {
  state.activeView = viewName;
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === `view-${viewName}`);
  });
  document.querySelectorAll("[data-view-target]").forEach((button) => {
    button.classList.toggle("active", button.dataset.viewTarget === viewName);
  });
  renderViewTitle();
  refreshActiveView();
  schedule();
}

async function refreshActiveView() {
  try {
    if (state.activeView === "lineb") {
      await loadLineBPanel();
    } else if (state.activeView === "runtime") {
      await loadRuntimePanel();
    } else if (state.activeView === "canvas") {
      await loadCanvasPanel();
    } else if (state.activeView === "memory") {
      await loadMemoryPanel();
    } else if (state.activeView === "graphiti") {
      await loadGraphitiPanel();
    } else {
      await loadStatus();
    }
  } catch (error) {
    renderActiveViewError(error);
  }
}

function activeRefreshMs() {
  if (state.activeView === "memory") return state.memoryRefreshMs;
  return state.refreshMs;
}

function schedule() {
  window.clearTimeout(state.timer);
  window.clearInterval(state.timer);
  state.timer = window.setTimeout(() => {
    if (state.paused) {
      schedule();
      return;
    }
    refreshActiveView().finally(schedule);
  }, activeRefreshMs());
}

function openSettings() {
  const dialog = $("settingsDialog");
  if (typeof dialog.showModal === "function") dialog.showModal();
  else dialog.setAttribute("open", "");
}

document.querySelectorAll("[data-view-target]").forEach((button) => {
  button.addEventListener("click", () => activateView(button.dataset.viewTarget));
});
$("refreshButton").addEventListener("click", refreshActiveView);
$("pauseButton").addEventListener("click", () => {
  state.paused = !state.paused;
  $("pauseButton").textContent = state.paused ? t("actions.resume") : t("actions.pause");
});
$("settingsButton").addEventListener("click", openSettings);
$("languageSelect").addEventListener("change", (event) => {
  state.language = event.target.value;
  localStorage.setItem("parrot.console.language", state.language);
  applyLanguage();
});
$("voiceRouteButton").addEventListener("click", setNoVideoRoute);
$("micCheckButton").addEventListener("click", checkMicrophone);
$("refreshProfilesButton").addEventListener("click", loadLineBPanel);
$("applyProfileButton").addEventListener("click", applyLineProfile);
$("registerTtsButton").addEventListener("click", registerTtsSegment);
$("submitMicButton").addEventListener("click", submitMicInput);
$("mintLiveKitButton").addEventListener("click", mintLiveKitToken);
$("connectLiveKitButton").addEventListener("click", connectLiveKitAudio);
$("disconnectLiveKitButton").addEventListener("click", disconnectLiveKitAudio);
$("triggerDraftButton").addEventListener("click", draftTriggerEvent);
$("triggerFireDryRunButton").addEventListener("click", fireTriggerDryRun);
$("messageCheckButton").addEventListener("click", dispatchMessageCheckDryRun);
$("messagePushButton").addEventListener("click", pushMessageDryRun);
document.querySelectorAll("[data-trigger-preset]").forEach((button) => {
  button.addEventListener("click", () => draftTriggerPreset(button.dataset.triggerPreset || "web_console_custom"));
});
$("memoryGraphMode").addEventListener("change", applyMemoryFilters);
$("memoryFilterApplyButton").addEventListener("click", applyMemoryFilters);
$("memoryUseSelectedButton").addEventListener("click", useSelectedMemoryNode);
$("memoryEdgeFromSelectedButton").addEventListener("click", () => setSelectedMemoryEdgeEndpoint("l2bEdgeFrom"));
$("memoryEdgeToSelectedButton").addEventListener("click", () => setSelectedMemoryEdgeEndpoint("l2bEdgeTo"));
$("memoryClearPreviewButton").addEventListener("click", clearMemoryDraftPreview);
$("memoryCanvasCreatePreviewButton").addEventListener("click", dryRunL2bNode);
$("memoryCanvasUseSelectedButton").addEventListener("click", useSelectedMemoryNode);
$("memoryCanvasEdgeFromButton").addEventListener("click", () => setSelectedMemoryEdgeEndpoint("l2bEdgeFrom"));
$("memoryCanvasEdgeToButton").addEventListener("click", () => setSelectedMemoryEdgeEndpoint("l2bEdgeTo"));
$("memoryCanvasDraftEdgeButton").addEventListener("click", draftL2bEdge);
$("memoryCanvasClearPreviewButton").addEventListener("click", clearMemoryDraftPreview);
$("l15BucketDraftButton").addEventListener("click", draftL15BucketOp);
$("l15BucketDryRunButton").addEventListener("click", dryRunL15BucketOp);
$("obsidianDraftButton").addEventListener("click", draftObsidianNode);
$("obsidianDryRunButton").addEventListener("click", dryRunObsidianNode);
$("l2bDraftButton").addEventListener("click", draftL2bNode);
$("l2bDryRunButton").addEventListener("click", dryRunL2bNode);
$("l2bUpdateButton").addEventListener("click", dryRunUpdateL2bNode);
$("l2bDeleteButton").addEventListener("click", dryRunDeleteL2bNode);
$("l2bEdgeDraftButton").addEventListener("click", draftL2bEdge);
$("l2bEdgeDryRunButton").addEventListener("click", dryRunL2bEdge);
$("graphitiSearchButton").addEventListener("click", searchGraphiti);
$("graphitiDraftButton").addEventListener("click", () => draftGraphitiEpisode(false));
$("graphitiDryRunButton").addEventListener("click", () => draftGraphitiEpisode(true));
window.addEventListener("beforeunload", () => {
  if (state.liveKitRoom) state.liveKitRoom.disconnect();
});
window.addEventListener("unhandledrejection", (event) => {
  event.preventDefault();
  renderActiveViewError(event.reason);
});

async function init() {
  applyLanguage();
  await loadConfig();
  await loadStatus();
  schedule();
}

init().catch((error) => {
  renderEnvelope({
    ok: false,
    state: "error",
    upstream: {},
    detail: { message: error instanceof Error ? error.message : String(error) },
    summary: {},
    status: null,
  });
});
