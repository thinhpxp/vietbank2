

/**
 * Simple Event Bus using Vue 3 Reactive system
 * Dùng để giao tiếp giữa các component/module không có quan hệ cha con (VD: auth.js -> App.vue)
 */
class EventBus {
    constructor() {
        this.events = new Map();
    }

    /**
     * Đăng ký lắng nghe sự kiện
     * @param {string} eventName 
     * @param {function} callback 
     */
    on(eventName, callback) {
        if (!this.events.has(eventName)) {
            this.events.set(eventName, []);
        }
        this.events.get(eventName).push(callback);
    }

    /**
     * Hủy đăng ký
     * @param {string} eventName 
     * @param {function} callback 
     */
    off(eventName, callback) {
        if (!this.events.has(eventName)) return;
        const callbacks = this.events.get(eventName);
        const index = callbacks.indexOf(callback);
        if (index !== -1) {
            callbacks.splice(index, 1);
        }
    }

    /**
     * Phát sự kiện
     * @param {string} eventName 
     * @param {*} data 
     */
    emit(eventName, data) {
        if (!this.events.has(eventName)) return;
        this.events.get(eventName).forEach(callback => callback(data));
    }
}

const eventBus = new EventBus();

// Định nghĩa các tên sự kiện globlal
export const EVENTS = {
    SHOW_GLOBAL_ERROR: 'show-global-error'
};

export default eventBus;
