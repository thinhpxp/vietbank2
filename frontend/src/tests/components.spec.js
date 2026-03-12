import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SvgIcon from '@/components/common/SvgIcon.vue'
import BaseModal from '@/components/BaseModal.vue'

describe('Shared Components', () => {

    describe('SvgIcon.vue', () => {
        it('should render correct icon by name', () => {
            const wrapper = mount(SvgIcon, {
                props: { name: 'user' }
            })
            // Check if it renders an svg with specific class
            expect(wrapper.classes()).toContain('svg-icon')
            // In SvgIcon, "user" icon has a circle and path
            expect(wrapper.find('circle').exists()).toBe(true)
        })

        it('should compute size correctly', () => {
            const wrapper = mount(SvgIcon, {
                props: { name: 'user', size: 'lg' }
            })
            expect(wrapper.attributes('width')).toBe('24')
            expect(wrapper.classes()).toContain('icon-lg')
        })

        it('should support custom numeric size', () => {
            const wrapper = mount(SvgIcon, {
                props: { name: 'user', size: 50 }
            })
            expect(wrapper.attributes('width')).toBe('50')
        })
    })

    describe('BaseModal.vue', () => {
        // Note: BaseModal uses Teleport to "body". 
        // In Vitest/JSDOM, we need to ensure "body" exists or mock Teleport.
        // Usually, mounting with global.stubs or just checking emitted events is enough.

        it('should emit close when close button is clicked', async () => {
            const wrapper = mount(BaseModal, {
                props: { isOpen: true, title: 'Test Modal' },
                global: {
                    stubs: {
                        Teleport: true // Stub teleport to keep content in wrapper for testing
                    }
                }
            })

            await wrapper.find('.btn-close').trigger('click')
            expect(wrapper.emitted()).toHaveProperty('close')
        })

        it('should handle resize logic (initial values)', async () => {
            const wrapper = mount(BaseModal, {
                props: { isOpen: true, initialWidth: 500, initialHeight: 400 },
                global: { stubs: { Teleport: true } }
            })

            const modalBox = wrapper.find('.modal-box')
            expect(modalBox.attributes('style')).toContain('width: 500px')
            expect(modalBox.attributes('style')).toContain('height: 400px')
        })

        it('should respect closeOnOverlay prop', async () => {
            const wrapper = mount(BaseModal, {
                props: { isOpen: true, closeOnOverlay: true },
                global: { stubs: { Teleport: true } }
            })

            await wrapper.find('.modal-overlay').trigger('click')
            expect(wrapper.emitted()).toHaveProperty('close')
        })
    })
})
