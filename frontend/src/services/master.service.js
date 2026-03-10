import api from './api';

const MasterService = {
    // Object Types
    getObjectTypes() {
        return api.get('/object-types/');
    },
    updateObjectType(id, data) {
        return api.put(`/object-types/${id}/`, data);
    },
    deleteObjectType(id) {
        return api.delete(`/object-types/${id}/`);
    },
    createObjectType(data) {
        return api.post('/object-types/', data);
    },

    // Groups
    getGroups() {
        return api.get('/groups/');
    },
    createGroup(data) {
        return api.post('/groups/', data);
    },
    updateGroup(id, data) {
        return api.put(`/groups/${id}/`, data);
    },
    deleteGroup(id) {
        return api.delete(`/groups/${id}/`);
    },

    // Fields
    getFields(params = {}) {
        return api.get('/fields/', { params });
    },
    getFieldsGrouped(entityType) {
        return api.get('/fields/active_fields_grouped/', {
            params: { entity_type: entityType }
        });
    },
    createField(data) {
        return api.post('/fields/', data);
    },
    updateField(id, data) {
        return api.put(`/fields/${id}/`, data);
    },
    deleteField(id) {
        return api.delete(`/fields/${id}/`);
    },

    // Form Views
    getFormViews() {
        return api.get('/form-views/');
    },
    createFormView(data) {
        return api.post('/form-views/', data);
    },
    updateFormView(id, data) {
        return api.put(`/form-views/${id}/`, data);
    },
    deleteFormView(id) {
        return api.delete(`/form-views/${id}/`);
    },

    // Roles
    getRoles() {
        return api.get('/roles/');
    },
    createRole(data) {
        return api.post('/roles/', data);
    },
    updateRole(id, data) {
        return api.put(`/roles/${id}/`, data);
    },
    deleteRole(id) {
        return api.delete(`/roles/${id}/`);
    },

    // Master Objects
    getAllObjects(params = {}) {
        return api.get('/master-objects/', { params });
    },

    getObjectById(id) {
        return api.get(`/master-objects/${id}/`);
    },

    createObject(data) {
        return api.post('/master-objects/', data);
    },

    updateObject(id, data) {
        return api.put(`/master-objects/${id}/`, data);
    },

    deleteObject(id) {
        return api.delete(`/master-objects/${id}/`);
    },

    bulkDeleteObjects(ids) {
        return api.post('/master-objects/bulk_delete/', { ids });
    },

    checkIdentity(objectType, key, value) {
        return api.get('/master-objects/check_identity/', {
            params: { object_type: objectType, key, value }
        });
    },

    // Document Templates
    getTemplates() {
        return api.get('/document-templates/');
    },
    createTemplate(formData) {
        return api.post('/document-templates/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    updateTemplate(id, data) {
        return api.patch(`/document-templates/${id}/`, data);
    },
    deleteTemplate(id) {
        return api.delete(`/document-templates/${id}/`);
    }
};

export default MasterService;
