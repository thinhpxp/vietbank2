<template>
    <Teleport to="body">
        <div v-if="visible" class="modal-overlay" :class="['overlay-' + overlayVariant]" @click.self="cancel">
            <div class="modal-box" :style="{ transform: `translate(${dragX}px, ${dragY}px)` }" ref="modalBox">
                <div class="modal-header" @mousedown="startDrag">
                    <h3>{{ title }}</h3>
                </div>
                <div class="modal-body">
                    <label>{{ label }}</label>
                    <input type="text" v-model="inputValue" class="input-control" @keyup.enter="confirm"
                        ref="inputRef" />
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
    name: 'InputModal',
    props: {
        visible: { type: Boolean, default: false },
        title: { type: String, default: 'Nhập thông tin' },
        label: { type: String, default: 'Tên:' },
        defaultValue: { type: String, default: '' },
        confirmText: { type: String, default: 'Xác nhận' },
        overlayVariant: { type: String, default: 'transparent' }
    },
    emits: ['confirm', 'cancel'],
    data() {
        return {
            inputValue: '',
            // Drag state
            isDragging: false,
            dragX: 0,
            dragY: 0,
            dragStartX: 0,
            dragStartY: 0,
            dragFrameId: null
        }
    },
    watch: {
        visible(newVal) {
            if (newVal) {
                this.inputValue = this.defaultValue;
                this.$nextTick(() => {
                    if (this.$refs.inputRef) {
                        this.$refs.inputRef.focus();
                        this.$refs.inputRef.select();
                    }
                });
            } else {
                // Reset position when closed
                this.dragX = 0;
                this.dragY = 0;
            }
        }
    },
    methods: {
        confirm() {
            if (this.inputValue.trim()) {
                this.$emit('confirm', this.inputValue.trim());
            }
        },
        cancel() {
            this.$emit('cancel');
        },
        // DRAG LOGIC
        startDrag(e) {
            // Only allow dragging from header
            if (e.target.closest('.modal-footer') || e.target.closest('.modal-body') || e.target.tagName === 'INPUT') return;

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
    width: 450px;
    max-width: 90%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    pointer-events: auto;
    will-change: transform;
}

.modal-header {
    padding: 15px 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    cursor: move;
    user-select: none;
}

.modal-header h3 {
    margin: 0;
    font-size: 18px;
    color: #333;
}

.modal-body {
    padding: 20px;
}

.modal-body label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
    color: #555;
}

.input-control {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.input-control:focus {
    outline: none;
    border-color: #42b983;
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
    background: #42b983;
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.btn-confirm:hover {
    background: #369870;
}
</style>
