import React from "react";
import {
  Composition,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";
import { Audio } from "@remotion/media";

// --- Color Palette ---
const BG_DARK = "#090A0F";

// --- SVG Icons ---
const AppleCursor: React.FC<{ size?: number }> = ({ size = 32 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path
      d="M4 3L11 20L14 13L21 10L4 3Z"
      fill="#FFFFFF"
      stroke="#000000"
      strokeWidth="1.5"
      strokeLinejoin="round"
    />
  </svg>
);

const TrafficLights: React.FC = () => (
  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F56" }} />
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FFBD2E" }} />
    <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#27C93F" }} />
  </div>
);

const CheckIcon: React.FC<{ size?: number; color?: string }> = ({ size = 20, color = "#10B981" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const GithubIcon: React.FC<{ size?: number }> = ({ size = 28 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="#FFFFFF">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
  </svg>
);

// --- SCENE 1: The Problem (Frames 0 - 130) ---
const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({ frame, fps, config: { damping: 12 } });
  const modalSpring = spring({ frame: frame - 20, fps, config: { damping: 14 } });
  const shake = frame > 45 && frame < 65 ? Math.sin(frame * 1.5) * 8 : 0;

  return (
    <div style={{
      width: "100%", height: "100%", display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", padding: "60px 40px",
      position: "relative", transform: `translateX(${shake}px)`
    }}>
      {/* Hook Typography */}
      <div style={{
        opacity: titleSpring,
        transform: `scale(${interpolate(titleSpring, [0, 1], [0.8, 1])})`,
        textAlign: "center", marginBottom: 50
      }}>
        <div style={{
          display: "inline-block", padding: "8px 24px", borderRadius: 999,
          background: "rgba(239, 68, 68, 0.15)", border: "1px solid rgba(239, 68, 68, 0.3)",
          color: "#F87171", fontSize: 24, fontWeight: 700, letterSpacing: 2, marginBottom: 20
        }}>
          THE AI WORKFLOW PROBLEM
        </div>
        <h1 style={{
          fontSize: 68, fontWeight: 900, color: "#FFFFFF", lineHeight: 1.1,
          margin: 0, textShadow: "0 10px 30px rgba(0,0,0,0.8)"
        }}>
          Hit your usage limit <br />
          <span style={{ color: "#EF4444" }}>AGAIN?</span>
        </h1>
      </div>

      {/* Mock ChatGPT Window with Rate Limit */}
      <div style={{
        width: 880, borderRadius: 24,
        background: "rgba(22, 24, 34, 0.95)", border: "1px solid rgba(255,255,255,0.1)",
        boxShadow: "0 30px 80px rgba(0,0,0,0.7), 0 0 40px rgba(239,68,68,0.2)",
        overflow: "hidden", opacity: modalSpring,
        transform: `translateY(${interpolate(modalSpring, [0, 1], [60, 0])}px)`
      }}>
        {/* Title bar */}
        <div style={{
          padding: "18px 24px", background: "rgba(30, 33, 46, 0.9)",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          borderBottom: "1px solid rgba(255,255,255,0.06)"
        }}>
          <TrafficLights />
          <div style={{ color: "#9CA3AF", fontSize: 16, fontWeight: 600 }}>ChatGPT — Personal</div>
          <div style={{ width: 40 }} />
        </div>

        {/* Content */}
        <div style={{ padding: "40px 36px", display: "flex", flexDirection: "column", gap: 24 }}>
          {/* User message */}
          <div style={{ alignSelf: "flex-end", maxWidth: "80%", background: "#2563EB", padding: "16px 24px", borderRadius: "20px 20px 4px 20px", color: "#FFF", fontSize: 22 }}>
            Refactor this production database pipeline...
          </div>

          {/* Rate limit banner */}
          <div style={{
            background: "rgba(239, 68, 68, 0.12)", border: "1.5px solid rgba(239, 68, 68, 0.4)",
            borderRadius: 18, padding: "28px 30px", display: "flex", flexDirection: "column", gap: 14
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#EF4444" }} />
              <div style={{ color: "#FCA5A5", fontSize: 24, fontWeight: 800 }}>
                You've hit your usage limit
              </div>
            </div>
            <p style={{ color: "#E2E8F0", fontSize: 20, margin: 0, lineHeight: 1.4 }}>
              Your rate limit resets in 3 hours. Upgrade or switch accounts to continue.
            </p>
          </div>

          {/* Frustrating login popup preview */}
          <div style={{
            background: "rgba(15, 17, 26, 0.9)", border: "1px dashed rgba(255,255,255,0.2)",
            borderRadius: 16, padding: "20px 24px", display: "flex", alignItems: "center", justifyContent: "space-between"
          }}>
            <span style={{ color: "#94A3B8", fontSize: 18 }}>Signing out & typing 2FA codes all day...</span>
            <span style={{ color: "#EF4444", fontWeight: 700, fontSize: 18 }}>❌ Exhausting</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- SCENE 2: The Solution - Meet Cloner (Frames 130 - 275) ---
const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 130;

  const headerSpring = spring({ frame: localFrame, fps, config: { damping: 12 } });
  const windowSpring = spring({ frame: localFrame - 15, fps, config: { damping: 14 } });

  const apps = [
    { name: "ChatGPT", icon: "🤖", color: "#10A37F" },
    { name: "Claude", icon: "✨", color: "#D97706" },
    { name: "Antigravity", icon: "⚡", color: "#3B82F6" },
    { name: "Gemini", icon: "💎", color: "#8B5CF6" },
  ];

  return (
    <div style={{
      width: "100%", height: "100%", display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", padding: "60px 40px",
      position: "relative"
    }}>
      {/* Title */}
      <div style={{
        opacity: headerSpring,
        transform: `scale(${interpolate(headerSpring, [0, 1], [0.85, 1])})`,
        textAlign: "center", marginBottom: 40
      }}>
        <div style={{
          display: "inline-block", padding: "8px 24px", borderRadius: 999,
          background: "rgba(59, 130, 246, 0.2)", border: "1px solid rgba(59, 130, 246, 0.4)",
          color: "#60A5FA", fontSize: 24, fontWeight: 700, letterSpacing: 2, marginBottom: 16
        }}>
          NATIVE MACOS APP
        </div>
        <h1 style={{
          fontSize: 80, fontWeight: 900, color: "#FFFFFF", lineHeight: 1.05, margin: 0,
          background: "linear-gradient(135deg, #FFFFFF 30%, #60A5FA 100%)",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
        }}>
          Meet Cloner
        </h1>
        <p style={{ color: "#94A3B8", fontSize: 28, marginTop: 12, fontWeight: 500 }}>
          Run multiple accounts simultaneously on your Mac
        </p>
      </div>

      {/* Cloner Window Mockup */}
      <div style={{
        width: 920, borderRadius: 28,
        background: "rgba(18, 20, 30, 0.95)", border: "1px solid rgba(255,255,255,0.12)",
        boxShadow: "0 40px 100px rgba(0,0,0,0.8), 0 0 60px rgba(59,130,246,0.25)",
        overflow: "hidden", opacity: windowSpring,
        transform: `translateY(${interpolate(windowSpring, [0, 1], [80, 0])}px)`
      }}>
        {/* Title bar */}
        <div style={{
          padding: "20px 28px", background: "rgba(25, 28, 42, 0.95)",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          borderBottom: "1px solid rgba(255,255,255,0.08)"
        }}>
          <TrafficLights />
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ color: "#FFF", fontSize: 18, fontWeight: 700 }}>Cloner</span>
            <span style={{ background: "#2563EB", color: "#FFF", fontSize: 12, fontWeight: 800, padding: "3px 8px", borderRadius: 6 }}>
              MULTI-ACCOUNT
            </span>
          </div>
          <span style={{ color: "#64748B", fontSize: 14 }}>18 AI Apps Detected</span>
        </div>

        {/* Content: Detected Apps */}
        <div style={{ padding: "40px 36px" }}>
          <div style={{ color: "#94A3B8", fontSize: 16, fontWeight: 700, letterSpacing: 1.5, marginBottom: 24 }}>
            CHOOSE AN APP TO CLONE
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20 }}>
            {apps.map((app, i) => {
              const cardSpring = spring({ frame: localFrame - 25 - i * 6, fps, config: { damping: 12 } });
              return (
                <div key={app.name} style={{
                  opacity: cardSpring,
                  transform: `scale(${interpolate(cardSpring, [0, 1], [0.8, 1])})`,
                  background: "rgba(30, 34, 52, 0.7)", border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 20, padding: "28px 20px", display: "flex", flexDirection: "column",
                  alignItems: "center", gap: 14, boxShadow: "0 10px 25px rgba(0,0,0,0.3)"
                }}>
                  <div style={{
                    width: 72, height: 72, borderRadius: 18, background: app.color,
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36,
                    boxShadow: `0 8px 20px ${app.color}40`
                  }}>
                    {app.icon}
                  </div>
                  <div style={{ color: "#FFF", fontSize: 20, fontWeight: 700 }}>{app.name}</div>
                  <div style={{
                    background: "rgba(59, 130, 246, 0.15)", color: "#60A5FA",
                    fontSize: 12, fontWeight: 800, padding: "4px 10px", borderRadius: 6
                  }}>
                    DETECTED
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- SCENE 3: The Interactive Demo - 1-Click Clone (Frames 275 - 435) ---
const Scene3: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 275;

  const modalSpring = spring({ frame: localFrame, fps, config: { damping: 14 } });
  
  // Cursor trajectory
  const cursorX = interpolate(localFrame, [0, 25, 45, 80, 110], [540, 280, 540, 680, 540], { extrapolateRight: "clamp" });
  const cursorY = interpolate(localFrame, [0, 25, 45, 80, 110], [1200, 600, 950, 1100, 1350], { extrapolateRight: "clamp" });
  const cursorClick = (localFrame > 24 && localFrame < 32) || (localFrame > 78 && localFrame < 86) || (localFrame > 108 && localFrame < 116);

  // Typewriter effect for "Work Account"
  const typedText = "Work Account".slice(0, Math.max(0, Math.floor((localFrame - 35) / 3)));
  const isCreated = localFrame >= 115;

  return (
    <div style={{
      width: "100%", height: "100%", display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", padding: "60px 40px",
      position: "relative"
    }}>
      {/* Title */}
      <div style={{ textAlign: "center", marginBottom: 30 }}>
        <h1 style={{ fontSize: 64, fontWeight: 900, color: "#FFFFFF", margin: 0 }}>
          1-Click Instant Clone
        </h1>
        <p style={{ color: "#94A3B8", fontSize: 24, marginTop: 8 }}>
          APFS Instant Copy • Zero Extra Disk Space • 100% Isolated
        </p>
      </div>

      {/* Modal Dialog */}
      <div style={{
        width: 820, borderRadius: 28,
        background: "rgba(20, 23, 36, 0.98)", border: "1.5px solid rgba(59, 130, 246, 0.4)",
        boxShadow: "0 40px 120px rgba(0,0,0,0.85), 0 0 80px rgba(59,130,246,0.25)",
        overflow: "hidden", opacity: modalSpring,
        transform: `scale(${interpolate(modalSpring, [0, 1], [0.9, 1])})`
      }}>
        {/* Header */}
        <div style={{
          padding: "24px 32px", borderBottom: "1px solid rgba(255,255,255,0.08)",
          display: "flex", justifyContent: "space-between", alignItems: "center"
        }}>
          <h2 style={{ fontSize: 26, fontWeight: 800, color: "#FFF", margin: 0 }}>
            Clone ChatGPT
          </h2>
          <span style={{ color: "#64748B", fontSize: 22 }}>✕</span>
        </div>

        {/* Body */}
        <div style={{ padding: "36px 32px", display: "flex", flexDirection: "column", gap: 28 }}>
          {/* Live Icon Preview with Badge */}
          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <div style={{ position: "relative" }}>
              <div style={{
                width: 90, height: 90, borderRadius: 22, background: "#10A37F",
                display: "flex", alignItems: "center", justifyContent: "center", fontSize: 44,
                boxShadow: "0 10px 25px rgba(16,163,127,0.3)"
              }}>
                🤖
              </div>
              {/* Badge */}
              <div style={{
                position: "absolute", bottom: -4, right: -4,
                width: 36, height: 36, borderRadius: "50%", background: "#3B82F6",
                border: "3px solid #141724", display: "flex", alignItems: "center",
                justifyContent: "center", color: "#FFF", fontSize: 13, fontWeight: 900
              }}>
                WO
              </div>
            </div>
            <div>
              <div style={{ color: "#FFF", fontSize: 24, fontWeight: 700 }}>ChatGPT (Work Account)</div>
              <div style={{ color: "#10B981", fontSize: 16, fontWeight: 600, marginTop: 4 }}>
                Ready to deploy on Desktop
              </div>
            </div>
          </div>

          {/* Profile Name Input */}
          <div>
            <label style={{ display: "block", color: "#94A3B8", fontSize: 16, fontWeight: 700, marginBottom: 10 }}>
              PROFILE NAME
            </label>
            <div style={{
              background: "rgba(11, 13, 20, 0.8)", border: "1.5px solid rgba(59, 130, 246, 0.5)",
              borderRadius: 14, padding: "18px 24px", color: "#FFF", fontSize: 24, fontWeight: 600
            }}>
              {typedText}
              <span style={{ opacity: Math.sin(frame * 0.3) > 0 ? 1 : 0, color: "#3B82F6" }}>|</span>
            </div>
          </div>

          {/* Color Palette */}
          <div>
            <label style={{ display: "block", color: "#94A3B8", fontSize: 16, fontWeight: 700, marginBottom: 12 }}>
              BADGE ACCENT COLOR
            </label>
            <div style={{ display: "flex", gap: 16 }}>
              {["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444", "#06B6D4"].map((c, i) => (
                <div key={c} style={{
                  width: 44, height: 44, borderRadius: "50%", background: c,
                  border: i === 0 ? "3px solid #FFF" : "none",
                  boxShadow: i === 0 ? `0 0 16px ${c}` : "none",
                  transform: i === 0 ? "scale(1.15)" : "scale(1)"
                }} />
              ))}
            </div>
          </div>

          {/* Action Button */}
          <div style={{
            marginTop: 10, borderRadius: 16, padding: "20px", textAlign: "center",
            background: isCreated ? "#10B981" : "#2563EB", color: "#FFF",
            fontSize: 24, fontWeight: 800, letterSpacing: 0.5,
            boxShadow: isCreated ? "0 10px 30px rgba(16,185,129,0.4)" : "0 10px 30px rgba(37,99,235,0.4)",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 12
          }}>
            {isCreated ? (
              <>
                <CheckIcon size={28} color="#FFF" />
                <span>Clone Created in Desktop/Cloner!</span>
              </>
            ) : (
              <span>Create Independent Clone</span>
            )}
          </div>
        </div>
      </div>

      {/* Simulated Cursor */}
      <div style={{
        position: "absolute", left: cursorX, top: cursorY,
        pointerEvents: "none", zIndex: 9999,
        transform: `scale(${cursorClick ? 0.85 : 1})`,
        transition: "transform 0.05s ease"
      }}>
        <AppleCursor size={42} />
      </div>
    </div>
  );
};

// --- SCENE 4: Side-by-Side Simultaneous Accounts & Outro (Frames 435 - 600) ---
const Scene4: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 435;

  const splitSpring = spring({ frame: localFrame, fps, config: { damping: 14 } });
  const outroOpacity = interpolate(localFrame, [100, 125], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div style={{
      width: "100%", height: "100%", display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", padding: "60px 30px",
      position: "relative"
    }}>
      {/* Split Screen Container */}
      <div style={{
        opacity: interpolate(localFrame, [0, 15, 95, 115], [0, 1, 1, 0], { extrapolateRight: "clamp" }),
        transform: `scale(${interpolate(splitSpring, [0, 1], [0.85, 1])})`,
        width: "100%", display: "flex", flexDirection: "column", alignItems: "center"
      }}>
        <h1 style={{ fontSize: 56, fontWeight: 900, color: "#FFFFFF", textAlign: "center", marginBottom: 30 }}>
          Two Accounts. <span style={{ color: "#3B82F6" }}>Zero Conflicts.</span>
        </h1>

        {/* Side-by-side Dual Windows */}
        <div style={{ display: "flex", gap: 20, width: "100%", justifyContent: "center" }}>
          {/* Left Window: Account A */}
          <div style={{
            width: 480, height: 600, borderRadius: 20,
            background: "rgba(22, 24, 34, 0.95)", border: "1px solid rgba(255,255,255,0.1)",
            boxShadow: "0 25px 60px rgba(0,0,0,0.6)", overflow: "hidden", display: "flex", flexDirection: "column"
          }}>
            <div style={{ padding: "14px 18px", background: "rgba(28, 31, 44, 0.95)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <TrafficLights />
              <span style={{ color: "#CBD5E1", fontSize: 14, fontWeight: 700 }}>ChatGPT (Personal)</span>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#EC4899" }} />
            </div>
            <div style={{ padding: 24, flex: 1, display: "flex", flexDirection: "column", gap: 14 }}>
              <div style={{ background: "#2563EB", padding: "12px 16px", borderRadius: 14, alignSelf: "flex-end", color: "#FFF", fontSize: 16 }}>
                Writing marketing copy for launch...
              </div>
              <div style={{ background: "rgba(255,255,255,0.06)", padding: "14px 16px", borderRadius: 14, color: "#94A3B8", fontSize: 15, lineHeight: 1.4 }}>
                Here are 5 viral hooks tailored for Instagram Reels...
              </div>
              <div style={{ marginTop: "auto", padding: "8px 12px", borderRadius: 8, background: "rgba(16,185,129,0.15)", color: "#34D399", fontSize: 13, fontWeight: 700 }}>
                ● Account 1 Active (Plus)
              </div>
            </div>
          </div>

          {/* Right Window: Account B */}
          <div style={{
            width: 480, height: 600, borderRadius: 20,
            background: "rgba(20, 24, 38, 0.95)", border: "1.5px solid rgba(59,130,246,0.5)",
            boxShadow: "0 25px 60px rgba(59,130,246,0.25)", overflow: "hidden", display: "flex", flexDirection: "column"
          }}>
            <div style={{ padding: "14px 18px", background: "rgba(24, 30, 50, 0.95)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <TrafficLights />
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ color: "#FFF", fontSize: 14, fontWeight: 800 }}>ChatGPT (Work)</span>
                <span style={{ background: "#3B82F6", color: "#FFF", fontSize: 10, fontWeight: 900, padding: "2px 6px", borderRadius: 4 }}>WO</span>
              </div>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#3B82F6" }} />
            </div>
            <div style={{ padding: 24, flex: 1, display: "flex", flexDirection: "column", gap: 14 }}>
              <div style={{ background: "#1E40AF", padding: "12px 16px", borderRadius: 14, alignSelf: "flex-end", color: "#FFF", fontSize: 16 }}>
                Generate PostgreSQL migration schema...
              </div>
              <div style={{ background: "rgba(59,130,246,0.08)", padding: "14px 16px", borderRadius: 14, color: "#93C5FD", fontSize: 15, lineHeight: 1.4, fontFamily: "monospace" }}>
                CREATE TABLE isolated_clones (...);
              </div>
              <div style={{ marginTop: "auto", padding: "8px 12px", borderRadius: 8, background: "rgba(59,130,246,0.2)", color: "#60A5FA", fontSize: 13, fontWeight: 700 }}>
                ● Account 2 Active (Work)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* OUTRO & CALL TO ACTION */}
      {localFrame >= 95 && (
        <div style={{
          position: "absolute", inset: 0, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", padding: "60px 40px",
          opacity: outroOpacity, transform: `scale(${interpolate(outroOpacity, [0, 1], [0.9, 1])})`
        }}>
          {/* Logo */}
          <div style={{
            width: 140, height: 140, borderRadius: 36,
            background: "linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)",
            border: "2px solid rgba(255,255,255,0.2)", display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 72, boxShadow: "0 20px 60px rgba(59,130,246,0.5)",
            marginBottom: 30
          }}>
            👥
          </div>

          <h1 style={{
            fontSize: 72, fontWeight: 900, color: "#FFFFFF", textAlign: "center", margin: 0,
            lineHeight: 1.1
          }}>
            Download Cloner
          </h1>
          <p style={{ color: "#94A3B8", fontSize: 28, marginTop: 14, marginBottom: 40, fontWeight: 600 }}>
            Free & Open Source for macOS
          </p>

          {/* GitHub Card */}
          <div style={{
            width: 720, borderRadius: 20, padding: "24px 32px",
            background: "rgba(22, 27, 34, 0.9)", border: "1px solid rgba(255,255,255,0.15)",
            boxShadow: "0 20px 50px rgba(0,0,0,0.6)", display: "flex", alignItems: "center",
            justifyContent: "space-between", marginBottom: 30
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
              <GithubIcon size={44} />
              <div>
                <div style={{ color: "#FFF", fontSize: 24, fontWeight: 800 }}>IBahaaaldin / Cloner</div>
                <div style={{ color: "#8B949E", fontSize: 16 }}>macOS Multi-Account AI App Manager</div>
              </div>
            </div>
            <div style={{
              background: "rgba(255,255,255,0.1)", borderRadius: 10, padding: "8px 18px",
              display: "flex", alignItems: "center", gap: 8, color: "#F0F6FC", fontSize: 18, fontWeight: 700
            }}>
              ★ Star
            </div>
          </div>

          {/* Watermark Branding */}
          <div style={{
            marginTop: 20, color: "#64748B", fontSize: 20, fontWeight: 700, letterSpacing: 1
          }}>
            BY BAHAA MOHAMMED • @IBAHAAALDINGCODING
          </div>
        </div>
      )}
    </div>
  );
};

// --- MAIN VIDEO ROOT COMPOSITION ---
export const ClonerPromoVideo: React.FC = () => {
  return (
    <div style={{
      width: 1080, height: 1920,
      background: BG_DARK, color: "#FFF",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif",
      overflow: "hidden", position: "relative"
    }}>
      {/* Background Ambience Mesh */}
      <div style={{
        position: "absolute", top: -200, left: -200, width: 800, height: 800,
        borderRadius: "50%", background: "radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%)",
        filter: "blur(80px)"
      }} />
      <div style={{
        position: "absolute", bottom: -200, right: -200, width: 800, height: 800,
        borderRadius: "50%", background: "radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%)",
        filter: "blur(80px)"
      }} />

      {/* Background Music Track (ducks softly across the whole video) */}
      <Audio src={staticFile("audio/bgm.mp3")} volume={0.28} />

      {/* --- SCENE 1 --- */}
      <Sequence from={0} durationInFrames={130}>
        <Scene1 />
        <Audio src={staticFile("audio/scene1.mp3")} volume={1.0} />
      </Sequence>
      {/* SFX: Error buzz when rate limit appears */}
      <Sequence from={24} durationInFrames={30}>
        <Audio src={staticFile("audio/error.mp3")} volume={0.6} />
      </Sequence>

      {/* --- SCENE 2 --- */}
      <Sequence from={130} durationInFrames={145}>
        <Scene2 />
        <Audio src={staticFile("audio/scene2.mp3")} volume={1.0} />
      </Sequence>
      {/* SFX: Whoosh at transition */}
      <Sequence from={128} durationInFrames={20}>
        <Audio src={staticFile("audio/whoosh.mp3")} volume={0.5} />
      </Sequence>
      <Sequence from={155} durationInFrames={25}>
        <Audio src={staticFile("audio/pop.mp3")} volume={0.4} />
      </Sequence>

      {/* --- SCENE 3 --- */}
      <Sequence from={275} durationInFrames={160}>
        <Scene3 />
        <Audio src={staticFile("audio/scene3.mp3")} volume={1.0} />
      </Sequence>
      {/* SFX: Click app, pop modal, click create, ding ready */}
      <Sequence from={274} durationInFrames={20}>
        <Audio src={staticFile("audio/whoosh.mp3")} volume={0.4} />
      </Sequence>
      <Sequence from={300} durationInFrames={15}>
        <Audio src={staticFile("audio/click.mp3")} volume={0.5} />
      </Sequence>
      <Sequence from={355} durationInFrames={15}>
        <Audio src={staticFile("audio/click.mp3")} volume={0.5} />
      </Sequence>
      <Sequence from={388} durationInFrames={15}>
        <Audio src={staticFile("audio/click.mp3")} volume={0.6} />
      </Sequence>
      <Sequence from={390} durationInFrames={40}>
        <Audio src={staticFile("audio/ding.mp3")} volume={0.7} />
      </Sequence>

      {/* --- SCENE 4 --- */}
      <Sequence from={435} durationInFrames={165}>
        <Scene4 />
        <Audio src={staticFile("audio/scene4.mp3")} volume={1.0} />
      </Sequence>
      {/* SFX: Whoosh into split screen */}
      <Sequence from={433} durationInFrames={20}>
        <Audio src={staticFile("audio/whoosh.mp3")} volume={0.5} />
      </Sequence>
      <Sequence from={540} durationInFrames={40}>
        <Audio src={staticFile("audio/ding.mp3")} volume={0.5} />
      </Sequence>
    </div>
  );
};

export const MyComposition = () => {
  return (
    <Composition
      id="ClonerPromo"
      component={ClonerPromoVideo}
      durationInFrames={600}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
