<template>
    <Teleport to="body">
        <div v-if="visible" class="modal-overlay" :class="['overlay-' + overlayVariant]" @click.self="handleOverlayClick">
            <div class="modal-box" :class="typeClass" :style="modalBoxStyle">
                <div class="modal-header" @mousedown="startDrag">
                    <span class="modal-icon">{{ iconEmoji }}</span>
                    <h3>{{ title }}</h3>
                </div>
                <div class="modal-body">
                    <p v-if="message" class="modal-message" v-html="message"></p>
                    <slot />

                    <!-- Error Code (nếu có) -->
                    <div v-if="errorCode" class="error-code">
                        <strong>Mã lỗi:</strong> {{ errorCode }}
                    </div>
                    
                    <!-- Nhập lý do (dùng cho xóa/khôi phục) -->
                    <div v-if="showReason" class="reason-section">
                        <label class="reason-label">{{ reasonLabel }}</label>
                        <textarea 
                            v-model="localReason" 
                            class="reason-textarea" 
                            :placeholder="reasonPlaceholder" 
                            rows="2"
                        ></textarea>
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
                    <button 
                        class="btn-confirm" 
                        :class="confirmButtonClass" 
                        :disabled="isConfirmDisabled"
                        @click="confirm"
                    >
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
        closeOnOverlay: { type: Boolean, default: false }, // Đóng khi click overlay
        overlayVariant: { type: String, default: 'transparent' }, // 'dim', 'light', 'transparent'
        showReason: { type: Boolean, default: false }, // Hiển thị ô nhập lý do
        reasonLabel: { type: String, default: 'Lý do thực hiện:' },
        reasonPlaceholder: { type: String, default: 'Nhập lý do tại đây...' }
    },
    emits: ['confirm', 'cancel'],
    data() {
        return {
            showDetails: false,
            timestamp: new Date().toLocaleString('vi-VN'),
            localReason: '', // Lưu giá trị lý do người dùng nhập
            // Drag state
            isDragging: false,
            dragX: 0,
            dragY: 0,
            dragStartX: 0,
            dragStartY: 0,
            dragFrameId: null
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
        },
        modalBoxStyle() {
            return {
                transform: `translate(${this.dragX}px, ${this.dragY}px)`
            };
        },
        isConfirmDisabled() {
            // Nếu có ô nhập lý do, yêu cầu không được để trống (sau khi trim)
            if (this.showReason) {
                return !this.localReason || this.localReason.trim().length === 0;
            }
            return false;
        }
    },
    methods: {
        confirm() {
            this.$emit('confirm', this.localReason);
        },
        cancel() {
            this.$emit('cancel');
        },
        handleOverlayClick() {
            if (this.closeOnOverlay) {
                this.cancel();
            }
        },
        // DRAG LOGIC
        startDrag(e) {
            this.isDragging = true;
            this.dragStartX = e.clientX - this.dragX;
            this.dragStartY = e.clientY - this.dragY;

            window.addEventListener('mousemove', this.doDrag);
            window.addEventListener('mouseup', this.stopDrag);
            document.body.style.userSelect = 'none';
        },
        doDrag(e) {
            if (!this.isDragging) return;
            const clientX = e.clientX;
            const clientY = e.clientY;

            if (this.dragFrameId) cancelAnimationFrame(this.dragFrameId);
            this.dragFrameId = requestAnimationFrame(() => {
                this.dragX = clientX - this.dragStartX;
                this.dragY = clientY - this.dragStartY;
            });
        },
        stopDrag() {
            this.isDragging = false;
            if (this.dragFrameId) cancelAnimationFrame(this.dragFrameId);
            window.removeEventListener('mousemove', this.doDrag);
            window.removeEventListener('mouseup', this.stopDrag);
            document.body.style.userSelect = '';
        }
    },
    beforeUnmount() {
        this.stopDrag();
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
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    transition: background 0.3s;
}

.modal-overlay.overlay-dim {
    background: rgba(0, 0, 0, 0.5);
}

.modal-overlay.overlay-light {
    background: rgba(0, 0, 0, 0.15);
}

.modal-overlay.overlay-transparent {
    background: transparent;
    pointer-events: none;
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
    pointer-events: auto;
    will-change: transform;
}

.modal-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 15px 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    cursor: move;
    user-select: none;
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

/* Reason Input */
.reason-section {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.reason-label {
    font-size: 14px;
    font-weight: 600;
    color: #333;
}

.reason-textarea {
    width: 100%;
    box-sizing: border-box;
    max-width: 100%;
    padding: 12px 15px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.5;
    resize: vertical;
    min-height: 80px;
    background: #ffffff;
    transition: all 0.2s ease-in-out;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
    color: #374151;
}

.reason-textarea::placeholder {
    color: #9ca3af;
    font-style: italic;
    font-size: 13px;
}

.reason-textarea:focus {
    outline: none;
    border-color: #3498db;
    background: #ffffff;
    box-shadow: 
        inset 0 1px 2px rgba(0, 0, 0, 0.05),
        0 0 0 4px rgba(52, 152, 219, 0.15);
}

.reason-textarea:hover {
    border-color: rgba(0, 0, 0, 0.2);
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
    transition: all 0.2s;
}

.btn-confirm:disabled {
    background: #ccc !important;
    cursor: not-allowed;
    opacity: 0.7;
    box-shadow: none !important;
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
