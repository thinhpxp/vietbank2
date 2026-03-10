import { describe, it, expect, vi, beforeEach } from 'vitest'
import MasterService from '@/services/master.service'
import api from '@/services/api'
import { mount } from '@vue/test-utils'
import MasterCreateModal from '@/components/MasterCreateModal.vue'

// Mock api service
vi.mock('@/services/api', () => ({
    default: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn()
    }
}))

// Mock Toast
const mockToast = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
}

describe('Locking Logic Tests', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    describe('MasterService Locking Methods', () => {
        it('acquireLock should call POST /master-objects/:id/acquire_lock/', async () => {
            api.post.mockResolvedValue({ data: { locked: false } })
            await MasterService.acquireLock(123)
            expect(api.post).toHaveBeenCalledWith('/master-objects/123/acquire_lock/')
        })

        it('releaseLock should call POST /master-objects/:id/release_lock/', async () => {
            await MasterService.releaseLock(123)
            expect(api.post).toHaveBeenCalledWith('/master-objects/123/release_lock/')
        })

        it('heartbeat should call POST /master-objects/:id/heartbeat/', async () => {
            await MasterService.heartbeat(123)
            expect(api.post).toHaveBeenCalledWith('/master-objects/123/heartbeat/')
        })
    })

    describe('MasterCreateModal Blocking Logic', () => {
        const defaultProps = {
            isOpen: true,
            type: 'PERSON',
            typeName: 'Cá nhân',
            editObject: { id: 123, field_values: { ho_ten: 'Test User' } },
            readOnly: true
        }

        it('should render warning message when readOnly is true', () => {
            const wrapper = mount(MasterCreateModal, {
                props: defaultProps,
                global: {
                    mocks: { $t: (msg) => msg, $toast: mockToast },
                    stubs: ['SvgIcon', 'DynamicForm', 'BaseModal']
                }
            })

            expect(wrapper.text()).toContain('Bạn hiện chỉ xem được thông tin, vì người khác đang chỉnh sửa đối tượng này')
        })

        it('should hide Save button when readOnly is true', () => {
            const wrapper = mount(MasterCreateModal, {
                props: defaultProps,
                global: {
                    mocks: { $t: (msg) => msg, $toast: mockToast },
                    stubs: ['SvgIcon', 'DynamicForm', 'BaseModal']
                }
            })

            const saveBtn = wrapper.find('.btn-save')
            expect(saveBtn.exists()).toBe(false)
        })

        it('should show Save button when readOnly is false', () => {
            const wrapper = mount(MasterCreateModal, {
                props: { ...defaultProps, readOnly: false },
                global: {
                    mocks: { $t: (msg) => msg, $toast: mockToast },
                    stubs: ['SvgIcon', 'DynamicForm', 'BaseModal']
                }
            })

            const saveBtn = wrapper.find('.btn-save')
            expect(saveBtn.exists()).toBe(true)
        })
    })
})
