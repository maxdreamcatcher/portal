/**
 * Portal-OS Cloudflare Worker Bootstrap
 * 
 * This is the entry point for Portal-OS running on Cloudflare Workers.
 * It:
 * 1. Initializes the runtime
 * 2. Handles incoming HTTP requests
 * 3. Routes them through the execution graph
 * 4. Manages Durable Object instances for long-lived compute
 * 5. Persists state to KV store
 */

import { PortalRuntime, createRuntime } from './runtime/index';

// Global runtime instance
let runtime: PortalRuntime | null = null;

/**
 * Initialize the runtime (called once per worker instance)
 */
async function initializeRuntime(env: any): Promise<PortalRuntime> {
  if (runtime) {
    return runtime;
  }

  runtime = createRuntime({
    mode: env.ENVIRONMENT === 'production' ? 'production' : 'development',
    cloudflareKV: env.PORTAL_KV,
    durableObjectNamespace: env.PORTAL_DO,
    env,
  });

  await runtime.boot();
  return runtime;
}

/**
 * Handle incoming HTTP requests
 */
async function handleRequest(request: Request, env: any, ctx: ExecutionContext): Promise<Response> {
  const rt = await initializeRuntime(env);
  const url = new URL(request.url);
  const path = url.pathname;
  const method = request.method;

  try {
    // Health check endpoint
    if (path === '/health' && method === 'GET') {
      const health = await rt.healthCheck();
      return new Response(JSON.stringify(health), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // System info endpoint
    if (path === '/system/info' && method === 'GET') {
      const state = rt.getState();
      return new Response(JSON.stringify(state), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Execute process endpoint
    if (path === '/execute' && method === 'POST') {
      const body = await request.json() as any;
      const { processName, entrypoint, context } = body;

      if (!processName || !entrypoint) {
        return new Response(
          JSON.stringify({ error: 'Missing processName or entrypoint' }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
      }

      try {
        const processId = await rt.executeProcess(processName, entrypoint, context);
        
        // Wait for process completion (with timeout)
        ctx.waitUntil(
          rt.getSubsystems().kernel.waitForProcess(processId, 25000)
            .then(result => {
              // Process completed successfully
              console.log(`Process ${processId} completed:`, result);
            })
            .catch(error => {
              // Process failed or timed out
              console.error(`Process ${processId} failed:`, error);
            })
        );

        return new Response(
          JSON.stringify({
            processId,
            status: 'queued',
            message: 'Process queued for execution',
          }),
          { status: 202, headers: { 'Content-Type': 'application/json' } }
        );
      } catch (error) {
        return new Response(
          JSON.stringify({ error: (error as Error).message }),
          { status: 500, headers: { 'Content-Type': 'application/json' } }
        );
      }
    }

    // Get process status
    if (path.startsWith('/process/') && method === 'GET') {
      const processId = path.replace('/process/', '');
      const subsystems = rt.getSubsystems();
      const process = subsystems.kernel.getProcess(processId);

      if (!process) {
        return new Response(
          JSON.stringify({ error: 'Process not found' }),
          { status: 404, headers: { 'Content-Type': 'application/json' } }
        );
      }

      return new Response(JSON.stringify(process), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // List all processes
    if (path === '/processes' && method === 'GET') {
      const subsystems = rt.getSubsystems();
      const processes = subsystems.kernel.getAllProcesses();

      return new Response(
        JSON.stringify({
          count: processes.length,
          processes: processes.map(p => ({
            processId: p.processId,
            processName: p.processName,
            status: p.status,
            createdAt: p.createdAt,
            startedAt: p.startedAt,
            completedAt: p.completedAt,
          })),
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Emit signal
    if (path === '/signal' && method === 'POST') {
      const body = await request.json() as any;
      const { signalType, payload } = body;

      if (!signalType) {
        return new Response(
          JSON.stringify({ error: 'Missing signalType' }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
      }

      await rt.emitSignal(signalType, payload || {});

      return new Response(
        JSON.stringify({ status: 'signal-emitted', signalType }),
        { status: 202, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Event history
    if (path === '/events' && method === 'GET') {
      const subsystems = rt.getSubsystems();
      const history = subsystems.eventBus.getHistory(undefined, 100);

      return new Response(
        JSON.stringify({
          count: history.length,
          events: history,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // 404
    return new Response(
      JSON.stringify({
        error: 'Not found',
        path,
        availableEndpoints: [
          'GET /health',
          'GET /system/info',
          'POST /execute',
          'GET /process/:processId',
          'GET /processes',
          'POST /signal',
          'GET /events',
        ],
      }),
      { status: 404, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Request handling error:', error);
    return new Response(
      JSON.stringify({
        error: 'Internal server error',
        message: (error as Error).message,
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

/**
 * Durable Object for Portal-OS Substrate
 * Long-lived compute and state management
 */
export class PortalSubstrateObject {
  private state: DurableObjectState;
  private env: any;
  private runtime: PortalRuntime | null = null;

  constructor(state: DurableObjectState, env: any) {
    this.state = state;
    this.env = env;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    try {
      // Initialize runtime if needed
      if (!this.runtime) {
        this.runtime = await initializeRuntime(this.env);
      }

      // Store data
      if (path === '/store' && method === 'POST') {
        const body = await request.json() as any;
        const { key, value } = body;

        if (!key) {
          return new Response(
            JSON.stringify({ error: 'Missing key' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }

        await this.state.storage.put(key, JSON.stringify(value));

        return new Response(
          JSON.stringify({ status: 'stored', key }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        );
      }

      // Retrieve data
      if (path === '/retrieve' && method === 'GET') {
        const key = url.searchParams.get('key');

        if (!key) {
          return new Response(
            JSON.stringify({ error: 'Missing key parameter' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }

        const value = await this.state.storage.get(key);

        if (value === undefined) {
          return new Response(
            JSON.stringify({ error: 'Key not found' }),
            { status: 404, headers: { 'Content-Type': 'application/json' } }
          );
        }

        return new Response(
          JSON.stringify({ key, value: JSON.parse(value as string) }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        );
      }

      // List keys
      if (path === '/list' && method === 'GET') {
        const keys = await this.state.storage.list();

        return new Response(
          JSON.stringify({ keys: Array.from(keys.keys()) }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        );
      }

      // Delete key
      if (path === '/delete' && method === 'POST') {
        const body = await request.json() as any;
        const { key } = body;

        if (!key) {
          return new Response(
            JSON.stringify({ error: 'Missing key' }),
            { status: 400, headers: { 'Content-Type': 'application/json' } }
          );
        }

        await this.state.storage.delete(key);

        return new Response(
          JSON.stringify({ status: 'deleted', key }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        );
      }

      return new Response(
        JSON.stringify({
          error: 'Not found',
          path,
          availableEndpoints: [
            'POST /store',
            'GET /retrieve?key=...',
            'GET /list',
            'POST /delete',
          ],
        }),
        { status: 404, headers: { 'Content-Type': 'application/json' } }
      );
    } catch (error) {
      console.error('Durable Object error:', error);
      return new Response(
        JSON.stringify({
          error: 'Internal server error',
          message: (error as Error).message,
        }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
  }
}

/**
 * Main export: Cloudflare Worker fetch handler
 */
export default {
  async fetch(request: Request, env: any, ctx: ExecutionContext): Promise<Response> {
    return handleRequest(request, env, ctx);
  },

  // Durable Object export
  PortalSubstrateObject,
};
