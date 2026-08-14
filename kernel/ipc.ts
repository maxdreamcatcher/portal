/**
 * Portal-OS IPC (Inter-Process Communication)
 * 
 * Allows processes to send messages to each other.
 * Built on top of the event bus for async-safe communication.
 */

import { EventBus } from '../event_bus/bus';

export interface IPCMessage {
  id: string;
  from: string;
  to: string;
  type: string;
  payload: Record<string, any>;
  timestamp: number;
  replyTo?: string;
}

export class IPCBus {
  private eventBus: EventBus;
  private messageHandlers: Map<string, Set<(message: IPCMessage) => void>> = new Map();
  private pendingReplies: Map<string, { resolve: Function; reject: Function; timeout: NodeJS.Timeout }> = new Map();

  constructor(eventBus: EventBus) {
    this.eventBus = eventBus;
  }

  /**
   * Send a message from one process to another
   */
  async send(toProcessId: string, payload: Record<string, any>, fromProcessId?: string): Promise<void> {
    const message: IPCMessage = {
      id: `ipc:${Date.now()}:${Math.random().toString(36).substr(2, 9)}`,
      from: fromProcessId || 'system',
      to: toProcessId,
      type: payload.type || 'message',
      payload,
      timestamp: Date.now(),
    };

    // Dispatch through event bus
    await this.eventBus.publish(`ipc:${toProcessId}`, message);
  }

  /**
   * Send a message and wait for a reply
   */
  async sendAndWaitReply(
    toProcessId: string,
    payload: Record<string, any>,
    fromProcessId?: string,
    timeout: number = 5000
  ): Promise<Record<string, any>> {
    const message: IPCMessage = {
      id: `ipc:${Date.now()}:${Math.random().toString(36).substr(2, 9)}`,
      from: fromProcessId || 'system',
      to: toProcessId,
      type: payload.type || 'message',
      payload,
      timestamp: Date.now(),
    };

    // Send the message
    await this.eventBus.publish(`ipc:${toProcessId}`, message);

    // Wait for reply
    return new Promise((resolve, reject) => {
      const timeoutHandle = setTimeout(() => {
        this.pendingReplies.delete(message.id);
        reject(new Error(`IPC reply timeout for ${message.id}`));
      }, timeout);

      this.pendingReplies.set(message.id, {
        resolve,
        reject,
        timeout: timeoutHandle,
      });
    });
  }

  /**
   * Listen for messages to a process
   */
  listen(processId: string, handler: (message: IPCMessage) => void): () => void {
    if (!this.messageHandlers.has(processId)) {
      this.messageHandlers.set(processId, new Set());
    }

    const handlers = this.messageHandlers.get(processId)!;
    handlers.add(handler);

    // Subscribe to event bus
    const unsubscribe = this.eventBus.subscribe(`ipc:${processId}`, (eventPayload: any) => {
      handler(eventPayload as IPCMessage);
    });

    // Return combined unsubscribe function
    return () => {
      handlers.delete(handler);
      unsubscribe();
      if (handlers.size === 0) {
        this.messageHandlers.delete(processId);
      }
    };
  }

  /**
   * Send a reply to an IPC message
   */
  async reply(originalMessage: IPCMessage, payload: Record<string, any>): Promise<void> {
    const replyMessage: IPCMessage = {
      id: `ipc:${Date.now()}:${Math.random().toString(36).substr(2, 9)}`,
      from: originalMessage.to,
      to: originalMessage.from,
      type: 'reply',
      payload,
      timestamp: Date.now(),
      replyTo: originalMessage.id,
    };

    // Check if this is being waited on
    const pending = this.pendingReplies.get(originalMessage.id);
    if (pending) {
      clearTimeout(pending.timeout);
      this.pendingReplies.delete(originalMessage.id);
      pending.resolve(payload);
    }

    // Also dispatch as event for listeners
    await this.eventBus.publish(`ipc:${originalMessage.from}`, replyMessage);
  }

  /**
   * Broadcast a message to all processes
   */
  async broadcast(payload: Record<string, any>, fromProcessId?: string): Promise<void> {
    for (const processId of this.messageHandlers.keys()) {
      await this.send(processId, payload, fromProcessId);
    }
  }

  /**
   * Get handlers for a process
   */
  getHandlerCount(processId: string): number {
    const handlers = this.messageHandlers.get(processId);
    return handlers ? handlers.size : 0;
  }

  /**
   * Get all listening processes
   */
  getListeningProcesses(): string[] {
    return Array.from(this.messageHandlers.keys());
  }
}
