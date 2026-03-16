import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import ObjectSelectModal from './ObjectSelectModal.vue'
import MasterService from '@/services/master.service'

// Mock MasterService
vi.mock('@/services/master.service', () => ({
  default: {
    getObjectTypes: vi.fn(),
    getAllObjects: vi.fn()
  }
}))

describe('ObjectSelectModal.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    MasterService.getObjectTypes.mockResolvedValue({ data: [] })
    MasterService.getAllObjects.mockResolvedValue({ data: [] })
  })

  it('gọi API getAllObjects với đúng tham số liên kết khi có relatedToSource', async () => {
    const wrapper = shallowMount(ObjectSelectModal, {
      props: {
        isOpen: true,
        type: 'attorney',
        relatedToSource: 123,
        relationType: 'REPRESENTATIVE'
      },
      global: {
        stubs: {
          BaseModal: true,
          SvgIcon: true,
          'vxe-table': true,
          'vxe-column': true
        },
        mocks: {
          $t: (msg) => msg
        }
      }
    })

    // Kích hoạt fetchItems trực tiếp
    await wrapper.vm.fetchItems()

    expect(MasterService.getAllObjects).toHaveBeenCalledWith(expect.objectContaining({
      related_to_source: 123,
      relation_type: 'REPRESENTATIVE'
    }))
  })

  it('không truyền tham số liên kết khi relatedToSource là null', async () => {
    const wrapper = shallowMount(ObjectSelectModal, {
      props: {
        isOpen: true,
        type: 'person',
        relatedToSource: null
      },
      global: {
        stubs: {
          BaseModal: true,
          SvgIcon: true,
          'vxe-table': true,
          'vxe-column': true
        },
        mocks: {
          $t: (msg) => msg
        }
      }
    })

    await wrapper.vm.fetchItems()

    expect(MasterService.getAllObjects).toHaveBeenCalledWith(expect.objectContaining({
      related_to_source: null
    }))
  })
})
