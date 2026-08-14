export default {
  async fetch(request: Request, env: any, ctx: ExecutionContext) {
    const url = new URL(request.url);
    const headers = { "Content-Type": "application/json" };

    // Health endpoints
    if (url.pathname.startsWith("/sim")) {
      return new Response(JSON.stringify({ sim: "SIM Core Online" }), { headers });
    }
    if (url.pathname.startsWith("/tec")) {
      return new Response(JSON.stringify({ tec: "TEC Orchestration Online" }), { headers });
    }
    if (url.pathname.startsWith("/identity")) {
      return new Response(JSON.stringify({ identity: "Identity Physics Online" }), { headers });
    }
    if (url.pathname.startsWith("/substrate")) {
      return new Response(JSON.stringify({ substrate: "Substrate Online" }), { headers });
    }

    // /api overview
    if (url.pathname === "/api" || url.pathname === "/api/") {
      return new Response(
        JSON.stringify({
          service: "Portal-OS Umbrella API",
          routes: ["/api/status", "/api/sim", "/api/tec", "/api/identity", "/api/substrate"]
        }),
        { headers }
      );
    }

    // /api/status
    if (url.pathname === "/api/status" || url.pathname === "/api/status/") {
      return new Response(
        JSON.stringify({
          status: "ok",
          uptime: "unknown",
          components: { sim: "online", tec: "online", identity: "online", substrate: "online" }
        }),
        { headers }
      );
    }

    // /api/sim
    if (url.pathname.startsWith("/api/sim")) {
      const parts = url.pathname.split("/").filter(Boolean);
      const id = parts.length >= 3 ? parts[2] : null;
      return new Response(JSON.stringify({ service: "sim", id, message: id ? `SIM ${id} OK` : "SIM root" }), { headers });
    }

    // /api/tec
    if (url.pathname.startsWith("/api/tec")) {
      const parts = url.pathname.split("/").filter(Boolean);
      const action = parts[2] || null;
      return new Response(JSON.stringify({ service: "tec", action, message: action ? `TEC action: ${action}` : "TEC root" }), { headers });
    }

    // /api/identity
    if (url.pathname.startsWith("/api/identity")) {
      return new Response(JSON.stringify({ service: "identity", info: "Identity Physics endpoint" }), { headers });
    }

    // --- /api/substrate: KV preferred, then Durable Object ---
    if (url.pathname.startsWith("/api/substrate")) {
      // GET -> read stored 'data'; POST -> store JSON payload
      if (request.method === "GET") {
        // Prefer KV if available
        if (env && env.SUBSTRATE_KV) {
          try {
            const data = await env.SUBSTRATE_KV.get("data", { type: "json" });
            return new Response(JSON.stringify({ source: "kv", data }), { headers });
          } catch (err: any) {
            // fallthrough to DO if KV fails
          }
        }
        // Fallback to Durable Object
        if (env && env.SUBSTRATE_DO) {
          const id = env.SUBSTRATE_DO.idFromName("default");
          const stub = env.SUBSTRATE_DO.get(id);
          // Forward original GET to DO
          return stub.fetch(request);
        }
        return new Response(JSON.stringify({ error: "no substrate binding configured" }), { headers, status: 404 });
      }

      if (request.method === "POST") {
        try {
          const body = await request.json();
          // Try KV
          if (env && env.SUBSTRATE_KV) {
            await env.SUBSTRATE_KV.put("data", JSON.stringify(body));
            return new Response(JSON.stringify({ stored: true, source: "kv" }), { headers });
          }
          // Else forward to Durable Object
          if (env && env.SUBSTRATE_DO) {
            const id = env.SUBSTRATE_DO.idFromName("default");
            const stub = env.SUBSTRATE_DO.get(id);
            const doReq = new Request("https://substrate.local/do", {
              method: "POST",
              body: JSON.stringify(body),
              headers: { "Content-Type": "application/json" }
            });
            return stub.fetch(doReq);
          }
          return new Response(JSON.stringify({ error: "no substrate binding configured" }), { headers, status: 404 });
        } catch (err: any) {
          return new Response(JSON.stringify({ error: err?.message || String(err) }), { headers, status: 500 });
        }
      }

      return new Response(JSON.stringify({ message: "use GET or POST on /api/substrate" }), { headers });
    }

    // Default fallback
    return new Response(JSON.stringify({ message: "Portal‑OS Worker Runtime Active" }), { headers });
  }
};
