
import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import RelationManager from '@/components/RelationManager.vue'

// Mock dependencies to avoid errors during mount
vi.mock('@/services/master.service', () => ({
  default: {
    searchMasterObjects: vi.fn(),
    getObjectById: vi.fn(() => Promise.resolve({ data: { relations_out: [], relations_in: [] } })),
  }
}))
vi.mock('@/services/relation.service', () => ({
  default: {
    getRelations: vi.fn(),
  }
}))

describe('RelationManager Whitelist Logic', () => {
  const profileObjects = [
    { id: 1, object_type: 'ALPHA', name: 'Alpha 1', allow_relations: true, is_restricted: true, allowed_relation_types_codes: ['BETA'], is_complete: true },
    { id: 2, object_type: 'BETA', name: 'Beta 1', allow_relations: true, is_restricted: false, allowed_relation_types_codes: [], is_complete: true },
    { id: 3, object_type: 'GAMMA', name: 'Gamma 1', allow_relations: true, is_restricted: false, allowed_relation_types_codes: [], is_complete: true },
  ]

  it('should only show BETA in whitelist for ALPHA source', async () => {
    const wrapper = shallowMount(RelationManager, {
      props: {
        masterObjectId: 1, // ALPHA
        profileObjects: profileObjects
      },
      global: {
        stubs: ['SvgIcon', 'ConfirmModal']
      }
    })

    // Wait for any async initializations if needed, although computed is sync
    const filtered = wrapper.vm.filteredPossibleTargets
    const types = filtered.map(o => o.object_type)
    
    expect(types).toContain('BETA')
    expect(types).not.toContain('GAMMA')
    expect(types).not.toContain('ALPHA') // Cannot link to self
  })

  it('should NOT show restricted ALPHA for GAMMA source (Public source)', async () => {
    const wrapper = shallowMount(RelationManager, {
      props: {
        masterObjectId: 3, // GAMMA
        profileObjects: profileObjects
      },
      global: {
        stubs: ['SvgIcon', 'ConfirmModal']
      }
    })

    const filtered = wrapper.vm.filteredPossibleTargets
    const types = filtered.map(o => o.object_type)
    
    expect(types).toContain('BETA')
    expect(types).not.toContain('ALPHA') // ALPHA is restricted and GAMMA is not authorized
  })
  
  it('should show both if public and no whitelist', async () => {
    const publicObjects = [
       { id: 10, object_type: 'PUB1', allow_relations: true, is_restricted: false, allowed_relation_types_codes: [], is_complete: true },
       { id: 11, object_type: 'PUB2', allow_relations: true, is_restricted: false, allowed_relation_types_codes: [], is_complete: true },
       { id: 12, object_type: 'PUB3', allow_relations: true, is_restricted: false, allowed_relation_types_codes: [], is_complete: true },
    ]
    const wrapper = shallowMount(RelationManager, {
      props: {
        masterObjectId: 10,
        profileObjects: publicObjects
      },
      global: {
        stubs: ['SvgIcon', 'ConfirmModal']
      }
    })
    
    const filtered = wrapper.vm.filteredPossibleTargets
    expect(filtered.length).toBe(2)
    expect(filtered.map(o => o.id)).toContain(11)
    expect(filtered.map(o => o.id)).toContain(12)
  })
})
