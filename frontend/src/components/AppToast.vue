<template>
    <div class="toast-container">
        <transition-group name="toast-fade">
            <div v-for="item in toastItems" :key="item.id" :class="['toast-item', item.type]"
                @click="removeToast(item.id)">
                <div class="toast-icon">
                    <span v-if="item.type === 'success'">✅</span>
                    <span v-else-if="item.type === 'error'">❌</span>
                    <span v-else-if="item.type === 'warning'">⚠️</span>
                    <span v-else>ℹ️</span>
                </div>
                <div class="toast-message">{{ item.message }}</div>
                <button class="toast-close" @click.stop="removeToast(item.id)">&times;</button>
            </div>
        </transition-group>
    </div>
</template>

<script>
import { toastState, toast } from '../utils/toast';

export default {
    name: 'AppToast',
    computed: {
        toastItems() {
            return toastState.items;
        }
    },
    methods: {
        removeToast(id) {
            toast.remove(id);
        }
    }
};
</script>

<style scoped>
.toast-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
    pointer-events: none;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 350px;
}

.toast-item {
    pointer-events: auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 250px;
    cursor: pointer;
    border-left: 4px solid #ccc;
    animation: slideIn 0.3s ease-out;
}

.toast-item.success {
    border-left-color: #2ecc71;
}

.toast-item.error {
    border-left-color: #e74c3c;
}

.toast-item.warning {
    border-left-color: #f1c40f;
}

.toast-item.info {
    border-left-color: #3498db;
}

.toast-icon {
    font-size: 1.2rem;
    flex-shrink: 0;
}

.toast-message {
    flex-grow: 1;
    font-size: 0.95rem;
    color: #333;
    text-align: left;
    line-height: 1.4;
}

.toast-close {
    background: none;
    border: none;
    font-size: 1.2rem;
    color: #999;
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
}

.toast-close:hover {
    color: #333;
}

/* Animations */
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }

    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast-fade-enter-active,
.toast-fade-leave-active {
    transition: all 0.3s ease;
}

.toast-fade-enter-from {
    transform: translateX(30px);
    opacity: 0;
}

.toast-fade-leave-to {
    transform: translateX(30px);
    opacity: 0;
}
</style>
