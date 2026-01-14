import { reactive } from 'vue';

export const toastState = reactive({
    items: []
});

let nextId = 1;

export const toast = {
    add(message, type = 'info', duration = 3000) {
        const id = nextId++;
        const item = { id, message, type };
        toastState.items.push(item);

        if (duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }
        return id;
    },

    success(message, duration) {
        return this.add(message, 'success', duration);
    },

    error(message, duration) {
        return this.add(message, 'error', duration);
    },

    info(message, duration) {
        return this.add(message, 'info', duration);
    },

    warning(message, duration) {
        return this.add(message, 'warning', duration);
    },

    remove(id) {
        const index = toastState.items.findIndex(item => item.id === id);
        if (index !== -1) {
            toastState.items.splice(index, 1);
        }
    }
};

// Plugin for Vue
export default {
    install: (app) => {
        app.config.globalProperties.$toast = toast;
    }
};
