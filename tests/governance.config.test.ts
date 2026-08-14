// tests/governance.config.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { createTestEnv } from './setup'
import { setBlockedWorkspacesKV, getBlockedWorkspaces, loadGovernanceConfig, setStrictMaintenanceFlagKV, getStrictMaintenanceFlag } from '../governance/config'

describe('governance/config KV persistence', () => {
  let env: any
  beforeEach(() => {
    env = createTestEnv()
  })

  it('persists and retrieves blocked workspaces', async () => {
    await setBlockedWorkspacesKV(env, ['ws1','ws2'])
    const list = await getBlockedWorkspaces(env)
    expect(list).toEqual(['ws1','ws2'])

    // loadGovernanceConfig returns applied values
    const loaded = await loadGovernanceConfig(env)
    expect(loaded?.blocked).toEqual(['ws1','ws2'])
  })

  it('sets and reads strict maintenance flag', async () => {
    await setStrictMaintenanceFlagKV(env, true)
    const v = await getStrictMaintenanceFlag(env)
    expect(v).toBe(true)
  })
})
