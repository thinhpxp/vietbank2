import { describe, it, expect } from 'vitest'
import { numberToWords, formatNumberVN, parseNumberVN } from '@/utils/formatters'

describe('formatters', () => {

    describe('numberToWords', () => {
        it('should convert integers correctly', () => {
            expect(numberToWords(1000)).toBe('Một nghìn')
            expect(numberToWords(1000000)).toBe('Một triệu')
            expect(numberToWords(1234)).toBe('Một nghìn hai trăm ba mươi bốn')
            expect(numberToWords(0)).toBe('Không')
        })

        it('should handle decimals', () => {
            expect(numberToWords(1.5)).toBe('Một phẩy năm')
        })

        it('should handle large numbers', () => {
            expect(numberToWords(123456789)).toBe('Một trăm hai mươi ba triệu bốn trăm năm mươi sáu nghìn bảy trăm tám mươi chín')
        })
    })

    describe('formatNumberVN', () => {
        it('should format numbers with dot as thousand separator', () => {
            expect(formatNumberVN(1000)).toBe('1.000')
            expect(formatNumberVN(1234567)).toBe('1.234.567')
        })

        it('should format decimals with comma', () => {
            expect(formatNumberVN(1234.56)).toBe('1.234,56')
        })
    })

    describe('parseNumberVN', () => {
        it('should parse VN format back to JS number string', () => {
            expect(parseNumberVN('1.234.567,89')).toBe('1234567.89')
        })
    })
})
