/* ════════════════════════════════════════════════════════════
 * script.js — HUD logic for the Surveillance Rover
 *
 * Sections:
 *   1. Helpers
 *   2. D-pad drive buttons  (discrete commands, hold-to-drive)
 *   3. Speed slider
 *   4. AI toggle
 *   5. Clock
 *   6. Telemetry loop       (FPS / objects / resolution / link status)
 *
 * The telemetry loop polls GET /telemetry once per second and
 * expects JSON: { "fps": 12.4, "objects": 2,
 *                 "resolution": "1280x720", "ai": true }
 * Until that route exists in app.py, the loop fails silently and
 * the HUD simply shows "--" — nothing else breaks.
 * ════════════════════════════════════════════════════════════ */

"use strict";

/* ───────────────────────── 1. HELPERS ───────────────────────── */

const $ = (id) => document.getElementById(id);

// Write text into an element if it exists (HUD stays optional-parts-safe)
function setText(id, text) {
  const el = $(id);
  if (el) el.textContent = text;
}

function send(cmd) {
  fetch("/" + cmd).catch(() => {}); // errors surface via the telemetry loop
}

/* ─────────────────── 2. D-PAD DRIVE BUTTONS ─────────────────── */
/* Pointer events cover mouse, touch, and pen with ONE code path —
 * no more separate mousedown/touchstart pairs. */

const DIRECTION_LABEL = {
  forward: "FWD",
  backward: "REV",
  left: "LEFT",
  right: "RIGHT",
  stop: "STOP",
};

function setDirection(cmd) {
  setText("direction", DIRECTION_LABEL[cmd] || cmd.toUpperCase());
}

function bindHoldButton(id, command) {
  const btn = $(id);
  if (!btn) return;

  let held = false;

  btn.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    btn.setPointerCapture(e.pointerId);
    held = true;
    send(command);
    setDirection(command);
  });

  const release = () => {
    if (!held) return;        // don't spam /stop if we weren't driving
    held = false;
    send("stop");
    setDirection("stop");
  };

  btn.addEventListener("pointerup", release);
  btn.addEventListener("pointercancel", release);
  btn.addEventListener("lostpointercapture", release);

  // Long-press on mobile tries to open a context menu — block it
  btn.addEventListener("contextmenu", (e) => e.preventDefault());
}

bindHoldButton("forward", "forward");
bindHoldButton("backward", "backward");
bindHoldButton("left", "left");
bindHoldButton("right", "right");

const stopBtn = $("stop");
if (stopBtn) {
  stopBtn.addEventListener("click", () => {
    send("stop");
    setDirection("stop");
  });
}

/* ─────────────────────── 3. SPEED SLIDER ─────────────────────── */

const slider = $("speedSlider");
if (slider) {
  slider.addEventListener("input", () => {
    const pct = slider.value + "%";
    setText("speedValue", pct);
    setText("speed-status", pct);
    fetch("/speed?value=" + slider.value / 100).catch(() => {});
  });
}

/* ──────────────────────── 4. AI TOGGLE ───────────────────────── */
/* Updates BOTH readouts: #ai-status (top bar) and #ai-state (bottom). */

function showAiState(on) {
  const label = on ? "ON" : "OFF";
  for (const id of ["ai-status", "ai-state"]) {
    const el = $(id);
    if (!el) continue;
    el.textContent = label;
    el.style.color = on ? "var(--green)" : "var(--text-dim)";
  }
}

$("ai-on")?.addEventListener("click", () => {
  fetch("/ai/on")
    .then(() => showAiState(true))
    .catch(() => {});
});

$("ai-off")?.addEventListener("click", () => {
  fetch("/ai/off")
    .then(() => showAiState(false))
    .catch(() => {});
});

/* ────────────────────────── 5. CLOCK ─────────────────────────── */

function tickClock() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  setText("clock", `${hh}:${mm}:${ss}`);
}
tickClock();
setInterval(tickClock, 1000);

/* ─────────────────────── 6. TELEMETRY LOOP ───────────────────── */
/* Polls the Pi once per second. Doubles as a connection monitor:
 * a few consecutive failures flips the HUD to OFFLINE. */

const TELEMETRY_INTERVAL = 1000;   // ms
const OFFLINE_AFTER = 3;           // consecutive failures

let telemetryFailures = 0;

function setLinkState(online) {
  const dot = $("online-dot");
  if (dot) {
    dot.style.background = online ? "var(--green)" : "var(--red)";
    dot.style.boxShadow = online
      ? "0 0 8px var(--green)"
      : "0 0 8px var(--red)";
  }
  setText("server-status", online ? "RUNNING" : "OFFLINE");
  const srv = $("server-status");
  if (srv) srv.style.color = online ? "var(--green)" : "var(--red)";
}

async function pollTelemetry() {
  try {
    const res = await fetch("/telemetry", { cache: "no-store" });
    if (!res.ok) throw new Error(res.status);
    const t = await res.json();

    telemetryFailures = 0;
    setLinkState(true);

    if (t.fps !== undefined) setText("fps", Number(t.fps).toFixed(1));
    if (t.objects !== undefined) {
      setText("object-count", t.objects);
      setText("objects-bottom", t.objects);
    }
    if (t.resolution) setText("resolution", t.resolution.replace("x", " × "));
    if (t.ai !== undefined) showAiState(!!t.ai); // stays true across reloads
  } catch {
    telemetryFailures++;
    if (telemetryFailures >= OFFLINE_AFTER) setLinkState(false);
    // Route not implemented yet or WiFi hiccup — HUD keeps working.
  }
}

pollTelemetry();
setInterval(pollTelemetry, TELEMETRY_INTERVAL);