// laya-guard for OpenCode — gates tool execution through a local judge.
//
// Install (project): copy to .opencode/plugins/laya-guard.ts
// Install (global):  copy to ~/.config/opencode/plugins/laya-guard.ts
// Needs: laya-guard server on localhost:8787 (laya-guard serve).
// Override: LAYA_GUARD_URL env (default http://localhost:8787/guard).
//
// Semantics: block -> throw (tool never runs). review -> allow + stderr
// warning, because tool.execute.before cannot trigger OpenCode's ask flow;
// use `permission` rules in opencode.json if you want hard asks.
// Guard unreachable -> fail open (returns silently).

const GUARD_URL = process.env.LAYA_GUARD_URL ?? "http://localhost:8787/guard";

async function judge(text: string): Promise<{ action: string; risk: number; policy_id: string; reason: string } | null> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 30000);
  try {
    const res = await fetch(GUARD_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool_call: text, source: "tool" }),
      signal: ctrl.signal,
    });
    if (!res.ok) return null;
    return (await res.json()) as { action: string; risk: number; policy_id: string; reason: string };
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export const LayaGuard = async () => ({
  "tool.execute.before": async (input: { tool: string }, output: { args: Record<string, unknown> }) => {
    const text =
      input.tool === "bash" && typeof output.args["command"] === "string"
        ? (output.args["command"] as string)
        : `${input.tool}(${JSON.stringify(output.args)})`;
    const v = await judge(text);
    if (v === null) return; // guard unreachable -> fail open
    if (v.action === "block") {
      throw new Error(`laya-guard blocked ${input.tool} [${v.policy_id} risk=${v.risk}]: ${v.reason}`);
    }
    if (v.action === "review") {
      console.error(`laya-guard review [${v.policy_id} risk=${v.risk}]: ${v.reason}`);
    }
  },
});
