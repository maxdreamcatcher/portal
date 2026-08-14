/**
 * Portal-OS v4.4 Worker
 * Multi-domain operating substrate deployed on Cloudflare Workers
 * 
 * Includes:
 * - SubstrateDO Durable Object
 * - KV namespace bindings (SUBSTRATE_KV, RUNTIME_KV)
 * - Routing layer (/health, /api/ping, /substrate/status)
 * - Portal-OS runtime
 */

// Types for Cloudflare bindings
interface Env {
  SUBSTRATE_KV = 807456cb41558d3c820308b20affa851
RUNTIME_KV = b9134f2c8d7e4a0fb2c1d9e6a4f7b812
SUBSTRATE_DO = SubstrateDO (class name)
}

/**
 * SubstrateDO - Durable Object for stateful substrate operations
 * Handles persistent state, transactions, and substrate logic
 */
export class SubstrateDO implements DurableObject {
  state: DurableObjectState
  env: Env

  constructor(state: DurableObjectState, env: Env) {
    this.state = state
    this.env = env
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url)
    const method = request.method

    // Substrate status endpoint
    if (url.pathname === '/status') {
      const state = await this.state.storage.get('substrate_state') || {}
      return new Response(
        JSON.stringify({
          status: 'ok',
          object: 'SubstrateDO',
          state,
          timestamp: new Date().toISOString(),
        }),
        {
          headers: { 'Content-Type': 'application/json' },
          status: 200,
        }
      )
    }

    // Substrate state get
    if (url.pathname === '/state' && method === 'GET') {
      const state = await this.state.storage.get('substrate_state')
      return new Response(
        JSON.stringify({
          state: state || {},
          timestamp: new Date().toISOString(),
        }),
        {
          headers: { 'Content-Type': 'application/json' },
          status: 200,
        }
      )
    }

    // Substrate state set
    if (url.pathname === '/state' && method === 'POST') {
      const body = await request.json()
      await this.state.storage.put('substrate_state', body)
      return new Response(
        JSON.stringify({
          status: 'ok',
          message: 'Substrate state updated',
          timestamp: new Date().toISOString(),
        }),
        {
          headers: { 'Content-Type': 'application/json' },
          status: 200,
        }
      )
    }

    return new Response(
      JSON.stringify({ error: 'Not Found', status: 404 }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 404,
      }
    )
  }
}

/**
 * Portal-OS v4.4 Worker
 * Main fetch handler for all routes and logic
 */
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)
    const method = request.method

    // Substrate Durable Object proxy
    if (url.pathname.startsWith('/substrate')) {
      try {
        const id = env.SUBSTRATE_DO.idFromName('default')
        const stub = env.SUBSTRATE_DO.get(id)
        
        // Forward request to DO
        const doRequest = new Request(new URL(url.pathname.replace('/substrate', ''), url.origin), {
          method,
          headers: request.headers,
          body: request.body,
        })
        
        return stub.fetch(doRequest)
      } catch (error) {
        return new Response(
          JSON.stringify({
            error: 'Durable Object error',
            message: error instanceof Error ? error.message : 'Unknown error',
          }),
          {
            headers: { 'Content-Type': 'application/json' },
            status: 500,
          }
        )
      }
    }

    // Health check endpoint
    if (url.pathname === '/health' && method === 'GET') {
      return new Response(
        JSON.stringify({
          status: 'healthy',
          service: 'Portal-OS v4.4',
          version: '4.4.0',
          timestamp: new Date().toISOString(),
        }),
        {
          headers: { 'Content-Type': 'application/json' },
          status: 200,
        }
      )
    }

    // API ping endpoint
    if (url.pathname === '/api/ping' && method === 'POST') {
      return new Response(
        JSON.stringify({
          status: 'ok',
          message: 'Runtime pinged. Portal-OS v4.4 responding.',
          timestamp: new Date().toISOString(),
        }),
        {
          headers: { 'Content-Type': 'application/json' },
          status: 200,
        }
      )
    }

    // KV test endpoint
    if (url.pathname === '/kv/test' && method === 'POST') {
      try {
        const testKey = 'portal-os-test'
        const testValue = { timestamp: new Date().toISOString(), test: true }
        
        await env.SUBSTRATE_KV.put(testKey, JSON.stringify(testValue))
        const retrieved = await env.SUBSTRATE_KV.get(testKey)
        
        return new Response(
          JSON.stringify({
            status: 'ok',
            message: 'KV test successful',
            written: testValue,
            retrieved: JSON.parse(retrieved || '{}'),
          }),
          {
            headers: { 'Content-Type': 'application/json' },
            status: 200,
          }
        )
      } catch (error) {
        return new Response(
          JSON.stringify({
            error: 'KV test failed',
            message: error instanceof Error ? error.message : 'Unknown error',
          }),
          {
            headers: { 'Content-Type': 'application/json' },
            status: 500,
          }
        )
      }
    }

    // Main dashboard/status page
    if (url.pathname === '/' && method === 'GET') {
      const html = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Portal-OS v4.4</title>
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              min-height: 100vh;
              display: flex;
              align-items: center;
              justify-content: center;
              padding: 20px;
            }
            .container {
              background: white;
              border-radius: 12px;
              box-shadow: 0 20px 60px rgba(0,0,0,0.3);
              padding: 50px;
              max-width: 700px;
              width: 100%;
            }
            h1 {
              color: #333;
              margin-bottom: 10px;
              font-size: 2.5em;
            }
            .subtitle {
              color: #666;
              font-size: 16px;
              margin-bottom: 30px;
            }
            .status-badge {
              display: inline-block;
              background: #10b981;
              color: white;
              padding: 12px 24px;
              border-radius: 24px;
              font-size: 14px;
              font-weight: 600;
              margin-bottom: 30px;
            }
            .section {
              margin-bottom: 40px;
            }
            .section-title {
              color: #333;
              font-size: 1.2em;
              font-weight: 600;
              margin-bottom: 15px;
              border-bottom: 2px solid #eee;
              padding-bottom: 10px;
            }
            .endpoint {
              background: #f9fafb;
              border-left: 4px solid #667eea;
              padding: 15px;
              margin-bottom: 10px;
              border-radius: 6px;
              font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
              font-size: 13px;
            }
            .method {
              color: #667eea;
              font-weight: 600;
              margin-right: 10px;
            }
            .path {
              color: #333;
            }
            .description {
              color: #666;
              font-size: 12px;
              margin-top: 5px;
            }
            .security-note {
              background: #fef3c7;
              border-left: 4px solid #f59e0b;
              padding: 15px;
              border-radius: 6px;
              font-size: 13px;
              color: #92400e;
              margin-top: 30px;
            }
            .features {
              display: grid;
              grid-template-columns: repeat(2, 1fr);
              gap: 15px;
              margin-top: 20px;
            }
            .feature {
              background: #f9fafb;
              padding: 15px;
              border-radius: 6px;
              font-size: 13px;
            }
            .feature strong {
              color: #667eea;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>🌐 Portal-OS v4.4</h1>
            <p class="subtitle">Multi-domain operating substrate on Cloudflare Workers</p>
            <div class="status-badge">✓ Online & Responding</div>
            
            <div class="section">
              <div class="section-title">Available Endpoints</div>
              
              <div class="endpoint">
                <div><span class="method">GET</span><span class="path">/</span></div>
                <div class="description">This page</div>
              </div>
              
              <div class="endpoint">
                <div><span class="method">GET</span><span class="path">/health</span></div>
                <div class="description">Service health check</div>
              </div>
              
              <div class="endpoint">
                <div><span class="method">POST</span><span class="path">/api/ping</span></div>
                <div class="description">Runtime ping verification</div>
              </div>
              
              <div class="endpoint">
                <div><span class="method">GET</span><span class="path">/substrate/status</span></div>
                <div class="description">Substrate Durable Object status</div>
              </div>
              
              <div class="endpoint">
                <div><span class="method">GET</span><span class="path">/substrate/state</span></div>
                <div class="description">Get substrate persistent state</div>
              </div>
              
              <div class="endpoint">
                <div><span class="method">POST</span><span class="path">/substrate/state</span></div>
                <div class="description">Update substrate persistent state</div>
              </div>
              
              <div class="endpoint">
                <div><span class="method">POST</span><span class="path">/kv/test</span></div>
                <div class="description">Test KV namespace functionality</div>
              </div>
            </div>
            
            <div class="section">
              <div class="section-title">Infrastructure</div>
              <div class="features">
                <div class="feature"><strong>Runtime:</strong> Cloudflare Workers</div>
                <div class="feature"><strong>State:</strong> Durable Objects</div>
                <div class="feature"><strong>Storage:</strong> KV Namespaces</div>
                <div class="feature"><strong>Version:</strong> 4.4.0</div>
              </div>
            </div>
            
            <div class="security-note">
              ✓ Dependencies secured and deployed on ${new Date().toISOString().split('T')[0]}
              <br>
              ✓ Durable Objects and KV namespaces configured and bound
            </div>
          </div>
        </body>
        </html>
      `
      
      return new Response(html, {
        headers: { 'Content-Type': 'text/html;charset=UTF-8' },
        status: 200,
      })
    }

    // 404 handler
    return new Response(
      JSON.stringify({
        error: 'Not Found',
        status: 404,
        path: url.pathname,
        message: 'Use GET / to see available endpoints',
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 404,
      }
    )
  },
            }
