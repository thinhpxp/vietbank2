<template>
    <Teleport to="body">
        <div v-if="visible" class="modal-overlay" @click.self="handleOverlayClick">
            <div class="modal-box" :class="typeClass">
                <div class="modal-header">
                    <span class="modal-icon">{{ iconEmoji }}</span>
                    <h3>{{ title }}</h3>
                </div>
                <div class="modal-body">
                    <p class="modal-message">{{ message }}</p>

                    <!-- Error Code (nếu có) -->
                    <div v-if="errorCode" class="error-code">
                        <strong>Mã lỗi:</strong> {{ errorCode }}
                    </div>

                    <!-- Chi tiết lỗi có thể mở rộng -->
                    <div v-if="details" class="error-details">
                        <button class="details-toggle" @click="showDetails = !showDetails" type="button">
                            {{ showDetails ? '▼' : '▶' }} Chi tiết kỹ thuật
                        </button>
                        <div v-if="showDetails" class="details-content">
                            <pre>{{ details }}</pre>
                        </div>
                    </div>

                    <!-- Timestamp (cho error tracking) -->
                    <div v-if="showTimestamp && type === 'error'" class="error-timestamp">
                        <small>Thời gian: {{ timestamp }}</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button v-if="mode === 'confirm'" class="btn-cancel" @click="cancel">
                        {{ cancelText }}
                    </button>
                    <button class="btn-confirm" :class="confirmButtonClass" @click="confirm">
                        {{ confirmText }}
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<script>
export default {
    name: 'ConfirmModal',
    props: {
        visible: { type: Boolean, default: false },
        title: { type: String, default: 'Xác nhận' },
        message: { type: String, default: 'Bạn có chắc chắn muốn thực hiện hành động này?' },
        confirmText: { type: String, default: 'Xác nhận' },
        cancelText: { type: String, default: 'Hủy' },
        mode: { type: String, default: 'confirm' }, // 'alert' hoặc 'confirm'
        type: { type: String, default: 'warning' }, // 'warning', 'error', 'success', 'info'
        errorCode: { type: String, default: '' }, // Mã lỗi (VD: "ERR_001")
        details: { type: String, default: '' }, // Chi tiết kỹ thuật (stack trace, JSON, etc.)
        showTimestamp: { type: Boolean, default: false }, // Hiển thị timestamp
        closeOnOverlay: { type: Boolean, default: false } // Đóng khi click overlay
    },
    emits: ['confirm', 'cancel'],
    data() {
        return {
            showDetails: false,
            timestamp: new Date().toLocaleString('vi-VN')
        };
    },
    computed: {
        iconEmoji() {
            const icons = {
                warning: '⚠️',
                error: '❌',
                success: '✅',
                info: 'ℹ️'
            };
            return icons[this.type] || icons.warning;
        },
        typeClass() {
            return `modal-${this.type}`;
        },
        confirmButtonClass() {
            const classes = {
                warning: 'btn-warning',
                error: 'btn-danger',
                success: 'btn-success',
                info: 'btn-primary'
            };
            return classes[this.type] || 'btn-warning';
        }
    },
    methods: {
        confirm() {
            this.$emit('confirm');
        },
        cancel() {
            this.$emit('cancel');
        },
        handleOverlayClick() {
            if (this.closeOnOverlay) {
                this.cancel();
            }
        }
    }
}
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.modal-box {
    background: #fff;
    border-radius: 8px;
    width: 500px;
    max-width: 90%;
    max-height: 80vh;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.modal-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 15px 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
}

.modal-icon {
    font-size: 24px;
}

/* Type-specific icon colors */
.modal-warning .modal-icon {
    color: #e67e22;
}

.modal-error .modal-icon {
    color: #e74c3c;
}

.modal-success .modal-icon {
    color: #27ae60;
}

.modal-info .modal-icon {
    color: #3498db;
}

.modal-header h3 {
    margin: 0;
    font-size: 18px;
    color: #333;
}

.modal-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
}

.modal-message {
    margin: 0 0 15px 0;
    color: #555;
    line-height: 1.5;
}

/* Error Code */
.error-code {
    padding: 10px;
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    margin-bottom: 15px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
}

/* Error Details (Expandable) */
.error-details {
    margin-top: 15px;
}

.details-toggle {
    background: none;
    border: none;
    color: #3498db;
    cursor: pointer;
    font-size: 14px;
    padding: 5px 0;
    text-align: left;
    width: 100%;
    display: flex;
    align-items: center;
    gap: 5px;
}

.details-toggle:hover {
    color: #2980b9;
    text-decoration: underline;
}

.details-content {
    margin-top: 10px;
    padding: 12px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    max-height: 200px;
    overflow-y: auto;
}

.details-content pre {
    margin: 0;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #333;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Timestamp */
.error-timestamp {
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #eee;
}

.error-timestamp small {
    color: #999;
    font-size: 12px;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 15px 20px;
    background: #f8f9fa;
    border-top: 1px solid #eee;
}

.btn-cancel {
    padding: 8px 16px;
    border: 1px solid #ccc;
    background: #fff;
    color: #555;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.btn-cancel:hover {
    background: #f0f0f0;
}

.btn-confirm {
    padding: 8px 16px;
    border: none;
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

/* Button variants */
.btn-warning {
    background: #e67e22;
}

.btn-warning:hover {
    background: #d35400;
}

.btn-danger {
    background: #e74c3c;
}

.btn-danger:hover {
    background: #c0392b;
}

.btn-success {
    background: #27ae60;
}

.btn-success:hover {
    background: #229954;
}

.btn-primary {
    background: #3498db;
}

.btn-primary:hover {
    background: #2980b9;
}
</style>
