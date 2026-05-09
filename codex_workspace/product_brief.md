# Product Brief

## One Sentence

GOSLOParrot is a personal Unity AR companion app backed by ParrotCarriers: a LiveKit + Redis + DSG + Nanobot bus that lets GOSLO see, talk, remember, dispatch work, and return useful notes into a playful 2D interface.

## User Intent

This is a personal demo first. It should feel direct, visible, and fun to use by its maker. It does not need generic onboarding polish or market-product explanation.

The app design should start from a small usable loop:

- normal 2D pixel boot/loading screen;
- transition directly into AR camera;
- a collapsible 2D pixel HUD in one corner;
- a collapsible 2D tool cabinet on the opposite corner;
- a 2D workspace inspired by document-review games for reports, calendar, feedback, and refs;
- paper-note feedback when Nanobot or Brain returns something important;
- all UI is Meta UI overlay, not physically integrated into the AR world.

## Core App Surfaces

### Unity AR App

Purpose: main embodied experience.

Core controls:

- camera mode / photo;
- focus or attention box;
- fly to hand;
- model/persona/mode/scene menu;
- basic task buttons;
- feedback paper notes.

Implementation home:

- `unity/ArSpike/Assets/Scripts/ParrotApp/`
- future UI assets: `unity/ArSpike/Assets/UI/`

### App 2D Workspace

Purpose: in-app paper desk for processing results, plans, calendar changes, and refs.

Initial scope:

- Nanobot report review;
- Google Calendar review/edit proposal;
- feedback notes expanded into readable documents;
- simple accept/reject/archive actions as UI stubs if writeback is not ready.

### Web Console

Purpose: developer visual debugger and configuration console.

Initial scope is read-only:

- DSG graph and buckets;
- Ref table;
- Blackboard/module status;
- IntentWorkspace state;
- menu registry and presets.

### Figma / Assets

Figma is a design source, not a blocker. Codex should create the Unity folder conventions and placeholder UI first, then replace with exported assets later.

## Existing Backend Capability

Already useful:

- LiveKit realtime layer;
- ECP DTO/event/command skeleton;
- Unity lifecycle/health/heartbeat scaffolding;
- GOSLO model manifest and controller abstraction;
- photo preview + upload path;
- Nanobot dispatch stream and result listener;
- DSG L1.5 buckets/ref table/timeline/scene snapshot concepts;
- Brain persona/menu/preset/IntentWorkspace direction is documented and partly implemented.

Main missing business layer:

- app startup flow and scene UI wiring;
- actual menu canvas UX;
- 2D workspace document flows;
- Google Calendar event format mapping and writeback;
- Nanobot result-to-report UI contract;
- Web console read APIs and front-end shell.

## Design Bias

- Build usable placeholders first.
- Put interactive controls where the user can see and test them.
- Keep the AR center clean.
- Do not overfit to existing app design because the front-end design is not settled.
- Treat Cursor docs as raw material, not a steering wheel.
