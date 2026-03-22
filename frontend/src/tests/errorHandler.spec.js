import { describe, it, expect, vi } from 'vitest'
import { formatError, getErrorMessage } from '@/utils/errorHandler'

// Mock translate
vi.mock('../utils/i18n', () => ({
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

        it('should format DRF field errors with prefix', () => {
            const error = {
                response: {
                    status: 400,
                    data: { username: ['This field is required'] }
                }
            }
            const result = formatError(error)
            expect(result.message).toContain('Dữ liệu nhập vào chưa hợp lệ')
            expect(result.message).toContain('This field is required')
        })

        it('should handle SimpleJWT token errors (global error with detail)', () => {
            const error = {
                response: {
                    status: 401,
                    data: {
                        detail: 'Given token not valid for any token type',
                        code: 'token_not_valid',
                        messages: [{ message: 'Token is invalid or expired' }]
                    }
                }
            }
            const result = formatError(error)
            // It should use detail and NOT be a bulleted list since detail is present
            expect(result.message).toBe('Given token not valid for any token type')
            expect(result.errorCode).toBe('token_not_valid')
        })

        it('should handle nested objects in field errors without [object Object]', () => {
            const error = {
                response: {
                    status: 400,
                    data: {
                        custom_field: [{ message: 'Nested error' }]
                    }
                }
            }
            const result = formatError(error)
            expect(result.message).toContain('Nested error')
            expect(result.message).not.toContain('[object Object]')
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
