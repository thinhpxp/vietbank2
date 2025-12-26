<template>
    <Teleport to="body">
        <div v-if="visible" class="modal-overlay" @click.self="cancel">
            <div class="modal-box">
                <div class="modal-header">
                    <span class="modal-icon">⚠</span>
                    <h3>{{ title }}</h3>
                </div>
                <div class="modal-body">
                    <p>{{ message }}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" @click="cancel">Hủy</button>
                    <button class="btn-confirm" @click="confirm">{{ confirmText }}</button>
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
        confirmText: { type: String, default: 'Xóa' }
    },
    emits: ['confirm', 'cancel'],
    methods: {
        confirm() {
            this.$emit('confirm');
        },
        cancel() {
            this.$emit('cancel');
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
    width: 400px;
    max-width: 90%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    overflow: hidden;
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
    color: #e67e22;
}

.modal-header h3 {
    margin: 0;
    font-size: 18px;
    color: #333;
}

.modal-body {
    padding: 20px;
}

.modal-body p {
    margin: 0;
    color: #555;
    line-height: 1.5;
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
    background: #e74c3c;
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.btn-confirm:hover {
    background: #c0392b;
}
</style>
