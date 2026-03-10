import api from './api';

const MasterRelationService = {
    createRelation(data) {
        return api.post('/master-relations/create_relation/', data);
    },

    deleteRelation(id) {
        return api.delete(`/master-relations/${id}/`);
    }
};

export default MasterRelationService;
