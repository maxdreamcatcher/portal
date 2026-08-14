// tests/setup.ts
// Test helpers: in-memory KV and test Env builder

import type { Env } from '../src/index'

export class MockKV {
  private store: Map<string, string>
  constructor() { this.store = new Map() }
  async get(key: string) { return this.store.get(key) ?? null }
  async put(key: string, value: string) { this.store.set(key, value) }
  async delete(key: string) { this.store.delete(key) }
  // simple list implementation returning an async iterator of pages (array)
  async *list(options: { prefix?: string } = {}) {
    const prefix = options.prefix || ''
    const entries = [...this.store.entries()].filter(([k]) => k.startsWith(prefix))
    // yield in pages of 50
    const pageSize = 50
    for (let i = 0; i < entries.length; i += pageSize) {
      const slice = entries.slice(i, i + pageSize).map(([k, v]) => ({ name: k, value: v }))
      yield slice
    }
  }
}

export function createTestEnv(): Env & { SUBSTRATE_KV: MockKV } {
  const kv = new MockKV()
  const env: any = {
    SUBSTRATE_DO: {} as DurableObjectNamespace,
    SUBSTRATE_KV: kv,
    RUNTIME_KV: kv,
    SUBSTRATE_ADMIN_SECRET: 'test-secret',
  }
  // attach for reactive module convenience
  ;(globalThis as any).__env__ = env
  return env
}
