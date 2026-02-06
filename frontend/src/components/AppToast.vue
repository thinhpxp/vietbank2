<template>
    <div class="toast-container">
        <transition-group name="toast-list">
            <div v-for="item in toastItems" :key="item.id" :class="['toast-item', item.type]" role="alert"
                @click="removeToast(item.id)">

                <div class="toast-content">
                    <div class="toast-icon-wrapper">
                        <SvgIcon :name="getIconName(item.type)" size="sm" stroke-width="2.5" />
                    </div>

                    <div class="toast-body">
                        <p class="toast-message">{{ item.message }}</p>
                    </div>

                    <button class="toast-close-btn" @click.stop="removeToast(item.id)" aria-label="Đóng">
                        <SvgIcon name="x" size="xs" />
                    </button>
                </div>

                <!-- Progress Bar -->
                <div v-if="item.duration > 0" class="toast-progress">
                    <div class="toast-progress-bar" :style="{ animationDuration: item.duration + 'ms' }">
                    </div>
                </div>
            </div>
        </transition-group>
    </div>
</template>

<script>
import { toastState, toast } from '../utils/toast';
import SvgIcon from './common/SvgIcon.vue';

export default {
    name: 'AppToast',
    components: {
        SvgIcon
    },
    computed: {
        toastItems() {
            return toastState.items;
        }
    },
    methods: {
        removeToast(id) {
            toast.remove(id);
        },
        getIconName(type) {
            switch (type) {
                case 'success': return 'check';
                case 'error': return 'x';
                case 'warning': return 'alert';
                case 'info': return 'info';
                default: return 'info';
            }
        }
    }
};
</script>

<style scoped>
.toast-container {
    position: fixed;
    top: 24px;
    right: 24px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
    max-width: 400px;
    pointer-events: none;
}

.toast-item {
    pointer-events: auto;
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow:
        0 4px 6px -1px rgba(0, 0, 0, 0.1),
        0 10px 15px -3px rgba(0, 0, 0, 0.1),
        inset 0 0 0 1px rgba(255, 255, 255, 0.5);
    padding: 16px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.toast-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.toast-content {
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.toast-icon-wrapper {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Color Themes */
.toast-item.success .toast-icon-wrapper {
    background: #ecfdf5;
    color: #10b981;
}

.toast-item.error .toast-icon-wrapper {
    background: #fef2f2;
    color: #ef4444;
}

.toast-item.warning .toast-icon-wrapper {
    background: #fffbeb;
    color: #f59e0b;
}

.toast-item.info .toast-icon-wrapper {
    background: #eff6ff;
    color: #3b82f6;
}

.toast-body {
    flex-grow: 1;
    padding-top: 4px;
}

.toast-message {
    margin: 0;
    font-size: 14px;
    font-weight: 500;
    color: #1f2937;
    line-height: 1.5;
}

.toast-close-btn {
    flex-shrink: 0;
    background: transparent;
    border: none;
    color: #9ca3af;
    padding: 4px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.toast-close-btn:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #4b5563;
}

/* Progress Bar */
.toast-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: rgba(0, 0, 0, 0.05);
}

.toast-progress-bar {
    height: 100%;
    width: 100%;
    background: currentColor;
    opacity: 0.6;
    transform-origin: left;
    animation: progress linear forwards;
}

.toast-item.success {
    color: #10b981;
}

.toast-item.error {
    color: #ef4444;
}

.toast-item.warning {
    color: #f59e0b;
}

.toast-item.info {
    color: #3b82f6;
}

@keyframes progress {
    from {
        transform: scaleX(1);
    }

    to {
        transform: scaleX(0);
    }
}

/* List Transitions */
.toast-list-enter-from {
    opacity: 0;
    transform: translateX(40px) scale(0.9);
}

.toast-list-leave-to {
    opacity: 0;
    transform: translateX(20px) scale(0.9);
}

.toast-list-leave-active {
    position: absolute;
}
</style>
