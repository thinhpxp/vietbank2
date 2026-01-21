<template>
    <Teleport to="body">
        <div v-if="isOpen" class="modal-overlay" @click.self="handleOverlayClick">
            <div class="modal-box" :style="modalStyle" ref="modalBox">
                <div class="modal-header">
                    <slot name="header">
                        <h3>{{ title }}</h3>
                    </slot>
                    <div class="header-actions">
                        <slot name="header-actions"></slot>
                        <button class="btn-close" @click="close">&times;</button>
                    </div>
                </div>

                <div class="modal-body">
                    <slot></slot>
                </div>

                <div v-if="$slots.footer" class="modal-footer">
                    <slot name="footer"></slot>
                </div>

                <!-- Resize Handle -->
                <div v-if="isResizable" class="resize-handle" @mousedown="startResize">
                    <div class="handle-icon"></div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<script>
export default {
    name: 'BaseModal',
    props: {
        isOpen: { type: Boolean, required: true },
        title: { type: String, default: 'Modal' },
        initialWidth: { type: [Number, String], default: 750 },
        initialHeight: { type: [Number, String], default: null },
        isResizable: { type: Boolean, default: true },
        minWidth: { type: Number, default: 400 },
        minHeight: { type: Number, default: 200 },
        closeOnOverlay: { type: Boolean, default: false }
    },
    emits: ['close'],
    data() {
        return {
            width: typeof this.initialWidth === 'number' ? this.initialWidth : null,
            height: typeof this.initialHeight === 'number' ? this.initialHeight : null,
            isResizing: false,
            startX: 0,
            startY: 0,
            startWidth: 0,
            startHeight: 0
        };
    },
    computed: {
        modalStyle() {
            const style = {};
            if (this.width) style.width = `${this.width}px`;
            else if (typeof this.initialWidth === 'string') style.width = this.initialWidth;

            if (this.height) style.height = `${this.height}px`;
            else if (typeof this.initialHeight === 'string') style.height = this.initialHeight;

            return style;
        }
    },
    methods: {
        close() {
            this.$emit('close');
        },
        handleOverlayClick() {
            if (this.closeOnOverlay) this.close();
        },
        startResize(e) {
            this.isResizing = true;
            this.startX = e.clientX;
            this.startY = e.clientY;

            const box = this.$refs.modalBox.getBoundingClientRect();
            this.startWidth = box.width;
            this.startHeight = box.height;

            window.addEventListener('mousemove', this.doResize);
            window.addEventListener('mouseup', this.stopResize);
            document.body.style.userSelect = 'none'; // Prevent text selection
        },
        doResize(e) {
            if (!this.isResizing) return;

            const deltaX = e.clientX - this.startX;
            const deltaY = e.clientY - this.startY;

            const newWidth = this.startWidth + deltaX;
            const newHeight = this.startHeight + deltaY;

            if (newWidth >= this.minWidth) {
                this.width = newWidth;
            }
            if (newHeight >= this.minHeight) {
                this.height = newHeight;
            }
        },
        stopResize() {
            this.isResizing = false;
            window.removeEventListener('mousemove', this.doResize);
            window.removeEventListener('mouseup', this.stopResize);
            document.body.style.userSelect = '';
        }
    },
    beforeUnmount() {
        this.stopResize();
    }
};
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9000;
}

.modal-box {
    background: white;
    max-width: 98vw;
    max-height: 95vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    animation: modalAppear 0.25s ease-out;
}

@keyframes modalAppear {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.95);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.modal-header {
    padding: 15px 25px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fcfcfc;
    flex-shrink: 0;
    cursor: default;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.btn-close {
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #bdc3c7;
    transition: color 0.2s;
    line-height: 1;
}

.btn-close:hover {
    color: #e74c3c;
}

.modal-body {
    flex: 1;
    padding: 25px;
    overflow-y: auto;
}

.modal-footer {
    padding: 15px 25px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    background: #f8f9fa;
    flex-shrink: 0;
}

/* Resize Handle Style */
.resize-handle {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 20px;
    height: 20px;
    cursor: nwse-resize;
    z-index: 10;
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    padding: 3px;
}

.handle-icon {
    width: 10px;
    height: 10px;
    border-right: 2px solid #ccc;
    border-bottom: 2px solid #ccc;
}

.resize-handle:hover .handle-icon {
    border-color: #3498db;
}
</style>
