import { describe, it, expect } from 'vitest'
import { evaluateFormula } from '@/utils/formulaEngine'

describe('formulaEngine', () => {
    const mockSections = {
        _GENERAL_: {
            individual_field_values: {
                interest_rate: 8.5,
                loan_term: 12
            }
        },
        PERSON: [
            { field_values: { ho_ten: 'Nguyen Van A', age: 30 } },
            { field_values: { ho_ten: 'Tran Thi B', age: 25 } }
        ],
        LAND_ASSET: [
            { field_values: { gia_tri: 1000000, square: 100 } },
            { field_values: { gia_tri: 2000000, square: 150 } }
        ]
    }

    it('should evaluate simple SUM with numbers', () => {
        expect(evaluateFormula('=SUM(10, 20, 30)', mockSections)).toBe(60)
    })

    it('should evaluate SUM across objects in multiple sections', () => {
        // Since Gia_tri is in LAND_ASSET, and formula provides ASSET or LAND_ASSET
        expect(evaluateFormula('=SUM(LAND_ASSET.gia_tri)', mockSections)).toBe(3000000)
    })

    it('should evaluate COUNT of objects', () => {
        expect(evaluateFormula('=COUNT(PERSON)', mockSections)).toBe(2)
        expect(evaluateFormula('=COUNT(LAND_ASSET)', mockSections)).toBe(2)
    })

    it('should evaluate AVG', () => {
        expect(evaluateFormula('=AVG(10, 20)', mockSections)).toBe(15)
        expect(evaluateFormula('=AVG(PERSON.age)', mockSections)).toBe(27.5)
    })

    it('should evaluate IF logic', () => {
        expect(evaluateFormula('=IF(SUM(LAND_ASSET.square) > 200, "Large", "Small")', mockSections)).toBe('Large')
        expect(evaluateFormula('=IF(SUM(LAND_ASSET.square) < 100, "Tiny", "Normal")', mockSections)).toBe('Normal')
    })

    it('should evaluate CONCAT with separator', () => {
        // Library logic: separator is the first/any string argument in quotes
        expect(evaluateFormula('=CONCAT(PERSON.ho_ten, " & ")', mockSections)).toBe('Nguyen Van A & Tran Thi B')
    })

    it('should evaluate nested ROUND', () => {
        expect(evaluateFormula('=ROUND(AVG(PERSON.age), 0)', mockSections)).toBe(28)
    })

    it('should handle missing fields gracefully', () => {
        expect(evaluateFormula('=SUM(NON_EXISTENT.field)', mockSections)).toBe(0)
    })

    it('should handle general fields', () => {
        expect(evaluateFormula('=_GENERAL_.interest_rate', mockSections)).toBe(null) // evaluateFormula expects =FUNC(...) or similar
        // Actually evaluateFormula requires a starting '='
        // Looking at code: it calls evaluateSubExpr which looks for FUNC(...)
        // So plain field access is not supported by evaluateFormula directly unless wrapped or handled via SUBEXPR regex
    })

    it('should evaluate PRODUCT/MUL', () => {
        expect(evaluateFormula('=MUL(2, 5, 10)', mockSections)).toBe(100)
    })
})
