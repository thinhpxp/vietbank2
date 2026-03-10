import { describe, it, expect, vi, beforeEach } from 'vitest'
import { formatError, getErrorMessage } from '@/utils/errorHandler'

// Mock translate
vi.mock('./i18n', () => ({
    translate: vi.fn(msg => msg)
}))

// Mock eventBus
vi.mock('./eventBus', () => ({
    default: {
        emit: vi.fn()
    },
    EVENTS: {
        SHOW_GLOBAL_ERROR: 'SHOW_GLOBAL_ERROR'
    }
}))

describe('errorHandler', () => {

    describe('formatError', () => {
        it('should format Axios response errors (object format)', () => {
            const error = {
                response: {
                    status: 400,
                    statusText: 'Bad Request',
                    data: { message: 'Invalid field' }
                }
            }
            const result = formatError(error)
            expect(result.message).toBe('Invalid field')
            expect(result.errorCode).toBe('HTTP_400')
        })

        it('should format DRF field errors', () => {
            const error = {
                response: {
                    status: 400,
                    data: { username: ['This field is required'] }
                }
            }
            const result = formatError(error)
            expect(result.message).toBe('This field is required')
        })

        it('should handle network errors', () => {
            const error = { request: {} }
            const result = formatError(error)
            expect(result.errorCode).toBe('NETWORK_ERROR')
        })

        it('should fallback for unknown errors', () => {
            const result = formatError({ message: 'Boom' })
            expect(result.message).toBe('Boom')
        })
    })

    describe('getErrorMessage', () => {
        it('should extract message from various objects', () => {
            expect(getErrorMessage('Simple Error')).toBe('Simple Error')
            expect(getErrorMessage({ response: { data: { message: 'API Error' } } })).toBe('API Error')
            expect(getErrorMessage({ message: 'JS Error' })).toBe('JS Error')
        })
    })
})
