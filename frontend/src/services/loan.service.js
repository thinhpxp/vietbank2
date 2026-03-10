import api from './api';

const LoanService = {
    getAll() {
        return api.get('/loan-profiles/');
    },

    getById(id) {
        return api.get(`/loan-profiles/${id}/`);
    },

    create(data) {
        return api.post('/loan-profiles/', data);
    },

    saveFormData(id, data) {
        return api.post(`/loan-profiles/${id}/save_form_data/`, data);
    },

    duplicate(id, newName) {
        return api.post(`/loan-profiles/${id}/duplicate/`, { new_name: newName });
    },

    lock(id, password) {
        return api.post(`/loan-profiles/${id}/lock_profile/`, { password });
    },

    unlock(id, password) {
        return api.post(`/loan-profiles/${id}/unlock_profile/`, { password });
    },

    acquireLock(id) {
        return api.post(`/loan-profiles/${id}/acquire_lock/`);
    },

    releaseLock(id) {
        return api.post(`/loan-profiles/${id}/release_lock/`);
    },

    heartbeat(id) {
        return api.post(`/loan-profiles/${id}/heartbeat/`);
    },

    getHistory(id) {
        return api.get(`/loan-profiles/${id}/history/`);
    },

    delete(id) {
        return api.delete(`/loan-profiles/${id}/`);
    }
};

export default LoanService;
