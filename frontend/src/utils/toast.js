import { reactive } from 'vue';

export const toastState = reactive({
    items: []
});

let nextId = 1;

export const toast = {
    lastMessage: null,
    lastType: null,
    lastTime: 0,

    add(message, type = 'info', duration = 3000) {
        const now = Date.now();
        // Debounce: Nếu cùng message và loại trong vòng 2s -> Bỏ qua
        if (this.lastMessage === message && this.lastType === type && (now - this.lastTime < 2000)) {
            return;
        }
        this.lastMessage = message;
        this.lastType = type;
        this.lastTime = now;

        const id = nextId++;
        const item = { id, message, type, duration };
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
