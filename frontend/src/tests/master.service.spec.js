import { describe, it, expect, vi, beforeEach } from 'vitest'
import MasterService from '@/services/master.service'
import api from '@/services/api'

// Mock api service
vi.mock('@/services/api', () => ({
    default: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn()
    }
}))

describe('MasterService', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('getObjectTypes should call GET /object-types/', async () => {
        const mockData = { data: [{ id: 1, name: 'Test' }] }
        api.get.mockResolvedValue(mockData)

        const result = await MasterService.getObjectTypes()

        expect(api.get).toHaveBeenCalledWith('/object-types/')
        expect(result).toEqual(mockData)
    })

    it('createObjectType should call POST /object-types/ with data', async () => {
        const newData = { code: 'NEW', name: 'New Type' }
        api.post.mockResolvedValue({ data: { id: 2, ...newData } })

        await MasterService.createObjectType(newData)

        expect(api.post).toHaveBeenCalledWith('/object-types/', newData)
    })

    it('getAllObjects should support params', async () => {
        const params = { search: 'test' }
        api.get.mockResolvedValue({ data: [] })

        await MasterService.getAllObjects(params)

        expect(api.get).toHaveBeenCalledWith('/master-objects/', { params })
    })
})
