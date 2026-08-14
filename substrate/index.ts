/**
 * Portal-OS Substrate Layer — Persistent State Management
 * 
 * The Substrate is where Portal-OS persists state:
 * - Cloudflare KV for fast key-value storage
 * - Durable Objects for long-lived compute and state
 * - Transactional semantics for consistency
 * 
 * Architecture:
 * - KVAdapter: Fast, distributed key-value store
 * - DurableObjectAdapter: Long-lived, single-threaded state
 * - SubstrateLayer: Unified interface above both
 */

export interface SubstrateConfig {
  kvNamespace?: any;
  durableObjectNamespace?: any;
}

export interface StorageEntry {
  key: string;
  value: any;
  storedAt: number;
  ttl?: number;
}

/**
 * KV Adapter for Cloudflare KV
 */
class KVAdapter {
  private kv: any;
  private prefix: string = 'portal:';

  constructor(kvNamespace: any) {
    this.kv = kvNamespace;
  }

  async set(key: string, value: any, ttl?: number): Promise<void> {
    const fullKey = `${this.prefix}${key}`;
    const metadata = {
      storedAt: Date.now(),
      ttl,
    };

    const options: any = { metadata };
    if (ttl) {
      options.expirationTtl = ttl;
    }

    await this.kv.put(fullKey, JSON.stringify(value), options);
  }

  async get(key: string): Promise<any> {
    const fullKey = `${this.prefix}${key}`;
    const value = await this.kv.get(fullKey, 'json');
    return value;
  }

  async delete(key: string): Promise<void> {
    const fullKey = `${this.prefix}${key}`;
    await this.kv.delete(fullKey);
  }

  async list(prefix?: string): Promise<string[]> {
    const listPrefix = prefix ? `${this.prefix}${prefix}` : this.prefix;
    const result = await this.kv.list({ prefix: listPrefix });
    return result.keys.map((k: any) => k.name.replace(this.prefix, ''));
  }

  async exists(key: string): Promise<boolean> {
    const value = await this.get(key);
    return value !== null && value !== undefined;
  }
}

/**
 * Durable Object Adapter
 * For long-lived, consistent state
 */
class DurableObjectAdapter {
  private doNamespace: any;
  private objectId: string = 'portal-substrate';

  constructor(doNamespace: any) {
    this.doNamespace = doNamespace;
  }

  private getStub() {
    const id = this.doNamespace.idFromName(this.objectId);
    return this.doNamespace.get(id);
  }

  async set(key: string, value: any): Promise<void> {
    const stub = this.getStub();
    await stub.fetch('https://internal/store', {
      method: 'POST',
      body: JSON.stringify({ key, value }),
    });
  }

  async get(key: string): Promise<any> {
    const stub = this.getStub();
    const response = await stub.fetch(`https://internal/retrieve?key=${encodeURIComponent(key)}`);
    const data = (await response.json()) as any;
    return data.value;
  }

  async delete(key: string): Promise<void> {
    const stub = this.getStub();
    await stub.fetch('https://internal/delete', {
      method: 'POST',
      body: JSON.stringify({ key }),
    });
  }

  async list(): Promise<string[]> {
    const stub = this.getStub();
    const response = await stub.fetch('https://internal/list');
    const data = (await response.json()) as any;
    return data.keys;
  }
}

/**
 * Unified Substrate Layer
 */
export class SubstrateLayer {
  private kvAdapter: KVAdapter | null;
  private doAdapter: DurableObjectAdapter | null;
  private isInitialized: boolean = false;
  private localCache: Map<string, { value: any; expiresAt: number }> = new Map();
  private cacheMaxSize: number = 1000;
  private cacheTTL: number = 60000; // 60 seconds default

  constructor(kvNamespace?: any, doNamespace?: any) {
    this.kvAdapter = kvNamespace ? new KVAdapter(kvNamespace) : null;
    this.doAdapter = doNamespace ? new DurableObjectAdapter(doNamespace) : null;
  }

  /**
   * Initialize the substrate
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    // Test connectivity
    if (this.kvAdapter) {
      try {
        await this.kvAdapter.set('__ping__', { timestamp: Date.now() }, 3600);
        await this.kvAdapter.get('__ping__');
      } catch (error) {
        console.warn('KV adapter connection test failed:', error);
      }
    }

    this.isInitialized = true;
  }

  /**
   * Write a value to substrate
   * Tries KV first, falls back to in-memory cache if unavailable
   */
  async write(key: string, value: any, options: { ttl?: number; durable?: boolean } = {}): Promise<void> {
    const { ttl = this.cacheTTL, durable = false } = options;

    try {
      // Try KV first (if available)
      if (this.kvAdapter && !durable) {
        await this.kvAdapter.set(key, value, ttl);
        this.updateCache(key, value, ttl);
        return;
      }

      // Use Durable Objects for critical state
      if (this.doAdapter && durable) {
        await this.doAdapter.set(key, value);
        this.updateCache(key, value, ttl);
        return;
      }

      // Fall back to in-memory cache
      this.updateCache(key, value, ttl);
    } catch (error) {
      console.error(`Failed to write key '${key}':`, error);
      // Still cache it locally even if write fails
      this.updateCache(key, value, ttl);
    }
  }

  /**
   * Read a value from substrate
   * Checks cache first, then KV, then Durable Objects
   */
  async read(key: string): Promise<any> {
    // Check cache first
    const cached = this.getFromCache(key);
    if (cached !== undefined) {
      return cached;
    }

    try {
      // Try KV
      if (this.kvAdapter) {
        const value = await this.kvAdapter.get(key);
        if (value !== null && value !== undefined) {
          this.updateCache(key, value);
          return value;
        }
      }

      // Try Durable Objects
      if (this.doAdapter) {
        const value = await this.doAdapter.get(key);
        if (value !== null && value !== undefined) {
          this.updateCache(key, value);
          return value;
        }
      }

      return undefined;
    } catch (error) {
      console.error(`Failed to read key '${key}':`, error);
      return undefined;
    }
  }

  /**
   * Delete a key
   */
  async delete(key: string): Promise<void> {
    this.localCache.delete(key);

    try {
      if (this.kvAdapter) {
        await this.kvAdapter.delete(key);
      }

      if (this.doAdapter) {
        await this.doAdapter.delete(key);
      }
    } catch (error) {
      console.error(`Failed to delete key '${key}':`, error);
    }
  }

  /**
   * List keys with optional prefix
   */
  async list(prefix?: string): Promise<string[]> {
    const results = new Set<string>();

    try {
      if (this.kvAdapter) {
        const kvKeys = await this.kvAdapter.list(prefix);
        kvKeys.forEach(k => results.add(k));
      }

      if (this.doAdapter) {
        const doKeys = await this.doAdapter.list();
        doKeys
          .filter(k => !prefix || k.startsWith(prefix))
          .forEach(k => results.add(k));
      }

      // Also add cached keys
      for (const key of this.localCache.keys()) {
        if (!prefix || key.startsWith(prefix)) {
          results.add(key);
        }
      }
    } catch (error) {
      console.error('Failed to list keys:', error);
    }

    return Array.from(results);
  }

  /**
   * Check if a key exists
   */
  async exists(key: string): Promise<boolean> {
    if (this.localCache.has(key)) {
      const entry = this.localCache.get(key)!;
      if (entry.expiresAt > Date.now()) {
        return true;
      }
      this.localCache.delete(key);
    }

    try {
      if (this.kvAdapter) {
        return await this.kvAdapter.exists(key);
      }
    } catch (error) {
      console.error(`Failed to check existence of key '${key}':`, error);
    }

    return false;
  }

  /**
   * Transaction: read-modify-write
   */
  async transaction<T>(
    key: string,
    modifier: (current: any) => T,
    options: { ttl?: number; durable?: boolean } = {}
  ): Promise<T> {
    const current = await this.read(key);
    const modified = modifier(current);
    await this.write(key, modified, options);
    return modified;
  }

  /**
   * Batch write
   */
  async batchWrite(
    entries: Array<{ key: string; value: any; ttl?: number }>,
    options: { durable?: boolean } = {}
  ): Promise<void> {
    await Promise.all(
      entries.map(entry =>
        this.write(entry.key, entry.value, {
          ttl: entry.ttl,
          durable: options.durable,
        })
      )
    );
  }

  /**
   * Batch read
   */
  async batchRead(keys: string[]): Promise<Record<string, any>> {
    const results: Record<string, any> = {};
    await Promise.all(
      keys.map(async key => {
        results[key] = await this.read(key);
      })
    );
    return results;
  }

  /**
   * Internal: Update local cache
   */
  private updateCache(key: string, value: any, ttl: number = this.cacheTTL): void {
    // Evict oldest entry if cache is full
    if (this.localCache.size >= this.cacheMaxSize) {
      const oldest = Array.from(this.localCache.entries()).reduce((min, entry) =>
        entry[1].expiresAt < min[1].expiresAt ? entry : min
      );
      this.localCache.delete(oldest[0]);
    }

    this.localCache.set(key, {
      value,
      expiresAt: Date.now() + ttl,
    });
  }

  /**
   * Internal: Get from cache if not expired
   */
  private getFromCache(key: string): any {
    const entry = this.localCache.get(key);
    if (!entry) {
      return undefined;
    }

    if (entry.expiresAt > Date.now()) {
      return entry.value;
    }

    this.localCache.delete(key);
    return undefined;
  }

  /**
   * Shutdown
   */
  async shutdown(): Promise<void> {
    this.localCache.clear();
    this.isInitialized = false;
  }

  /**
   * Health check
   */
  getHealth(): {
    initialized: boolean;
    kvAvailable: boolean;
    doAvailable: boolean;
    cacheSize: number;
  } {
    return {
      initialized: this.isInitialized,
      kvAvailable: !!this.kvAdapter,
      doAvailable: !!this.doAdapter,
      cacheSize: this.localCache.size,
    };
  }
}
