export class SubstrateDO {
  state: DurableObjectState;
  env: any;

  constructor(state: DurableObjectState, env: any) {
    this.state = state;
    this.env = env;
  }

  async fetch(request: Request) {
    const headers = { "Content-Type": "application/json" };
    const url = new URL(request.url);

    // POST stores arbitrary JSON at key `data`
    if (request.method === "POST") {
      try {
        const body = await request.json();
        await this.state.storage.put("data", body);
        return new Response(JSON.stringify({ stored: true }), { headers });
      } catch (err: any) {
        return new Response(JSON.stringify({ error: err?.message || String(err) }), { headers, status: 500 });
      }
    }

    // GET returns stored value
    const stored = await this.state.storage.get("data");
    return new Response(JSON.stringify({ stored }), { headers });
  }
}
