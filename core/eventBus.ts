// core/eventBus.ts
// Portal-OS v4.5 — Event Bus scaffold
// Purpose: lightweight, strongly-typed pub/sub for the runtime. Designed to be used
// inside the Worker runtime and can be extended to forward events to the
// Substrate Durable Object or KV for persistence / cross-worker delivery.

export type EventName =
  | 'sim.identity.updated'
  | 'sim.context.changed'
  | 'sim.goal.generated'
  | 'substrate.event'
  | 'governance.policy.check'
  | string

export interface Event<T = unknown> {
  name: EventName
  payload: T
  meta?: Record<string, unknown>
  timestamp: string
  workspace?: string
}

export type Handler<T = unknown> = (evt: Event<T>) => Promise<void> | void

export interface PersistentPublisher {
  // Implementations should persist/forward the event to a Durable Object, KV,
  // or external event-bus. Return a Promise that resolves when the event has
  // been durably recorded or forwarded.
  publish(evt: Event): Promise<void>
}

export class EventBus {
  private handlers: Map<string, Set<Handler>> = new Map()
  private persistentPublisher: PersistentPublisher | null = null

  // Subscribe to a specific event name (exact match) or to a wildcard '*'
  on(name: string, handler: Handler) {
    if (!this.handlers.has(name)) this.handlers.set(name, new Set())
    this.handlers.get(name)!.add(handler)
  }

  off(name: string, handler: Handler) {
    const s = this.handlers.get(name)
    if (!s) return
    s.delete(handler)
    if (s.size === 0) this.handlers.delete(name)
  }

  // Attach a persistent publisher (e.g. Substrate DO forwarder)
  attachPersistentPublisher(p: PersistentPublisher) {
    this.persistentPublisher = p
  }

  detachPersistentPublisher() {
    this.persistentPublisher = null
  }

  // Emit an event locally (invoke handlers) and optionally persist/forward it.
  async emit<T = unknown>(evt: Event<T>, opts: { persist?: boolean } = { persist: true }) {
    evt.timestamp = evt.timestamp || new Date().toISOString()

    // Local delivery: exact name and wildcard
    const deliver = async (name: string) => {
      const set = this.handlers.get(name)
      if (!set) return
      // Call handlers in parallel but wait for all to settle
      await Promise.allSettled(Array.from(set).map((h) => Promise.resolve(h(evt))))
    }

    // deliver exact
    await deliver(evt.name)
    // deliver wildcard
    await deliver('*')

    // Persist / forward if requested and publisher attached
    if (opts.persist && this.persistentPublisher) {
      try {
        await this.persistentPublisher.publish(evt)
      } catch (err) {
        // Non-fatal: log and continue. Consumers can subscribe to 'eventbus.error'.
        const errorEvent: Event = {
          name: 'eventbus.error',
          payload: { error: String(err), original: evt },
          timestamp: new Date().toISOString(),
        }
        // best-effort local delivery of error
        await Promise.allSettled(Array.from(this.handlers.get('eventbus.error') ?? [])
          .map((h) => Promise.resolve(h(errorEvent))))
      }
    }
  }

  // Convenience: subscribe once
  once(name: string, handler: Handler) {
    const wrapper: Handler = async (evt) => {
      try {
        await Promise.resolve(handler(evt))
      } finally {
        this.off(name, wrapper)
      }
    }
    this.on(name, wrapper)
  }
}

// Export a singleton EventBus for the runtime. Modules should import this and
// register handlers or attach a persistent publisher (e.g. a Substrate DO
// forwarder that implements PersistentPublisher).
export const eventBus = new EventBus()

// Example persistent publisher stub (to be implemented in substrate/events.ts):
//
// export class SubstrateDOPublisher implements PersistentPublisher {
//   constructor(private env: Env) {}
//   async publish(evt: Event) {
//     // Convert evt -> fetch to Durable Object or write to KV
//     const id = this.env.SUBSTRATE_DO.idFromName(evt.workspace || 'default')
//     const stub = this.env.SUBSTRATE_DO.get(id)
//     await stub.fetch(new Request('https://internal/ingest', {
//       method: 'POST',
//       body: JSON.stringify(evt),
//       headers: { 'Content-Type': 'application/json' },
//     }))
//   }
// }

// TODO: Add typed event schemas, metrics hooks, and backpressure handling.
