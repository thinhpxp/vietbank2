# BaseModal Integration Guide

The `BaseModal.vue` is a reusable, resizable modal component designed to provide a consistent look and feel across the application. It supports teleportation to the body, built-in resizing logic, and flexible content via slots.

## Location
`frontend/src/components/BaseModal.vue`

## Basic Usage

1. **Import and Register**:
```javascript
import BaseModal from '@/components/BaseModal.vue';

export default {
  components: { BaseModal },
  // ...
}
```

2. **Template Structure**:
```vue
<BaseModal 
    :isOpen="isModalOpen" 
    title="My Modal Title" 
    @close="isModalOpen = false"
>
    <!-- Default Slot: Modal Body -->
    <p>This is the body content.</p>

    <!-- Optional Footer Slot -->
    <template #footer>
        <button @click="isModalOpen = false">Close</button>
        <button @click="handleAction">Action</button>
    </template>

    <!-- Optional Header Actions Slot -->
    <template #header-actions>
        <button class="btn-icon">⭐</button>
    </template>
</BaseModal>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `isOpen` | Boolean | **Required** | Controls visibility. |
| `title` | String | 'Modal' | Text displayed in the header. |
| `initialWidth` | Number/String | 650 | Starting width in pixels. |
| `initialHeight` | Number/String | null | Starting height. If null, adapts to content. |
| `isResizable` | Boolean | true | Enables the resize handle. |
| `minWidth` | Number | 400 | Minimum allowed width when resizing. |
| `minHeight` | Number | 200 | Minimum allowed height when resizing. |
| `closeOnOverlay` | Boolean | false | If true, clicking the outside overlay closes the modal. |

## Slots

- **default**: The main body of the modal. This area is scrollable.
- **header**: Replaces the entire header content (replaces title, but keeps actions and close button unless customized).
- **header-actions**: Area to the left of the close [x] button for custom icons or buttons.
- **footer**: Fixed area at the bottom for action buttons (Cancel, Save, etc.).

## Best Practices
- **Fixed Height**: If you want the modal to have a fixed height from the start, pass `initialHeight`.
- **Large Content**: The modal body automatically scrolls if content exceeds the available height. Use that to your advantage for large forms.
- **Buttons**: Use standard class names like `btn-cancel` and `btn-save` within the footer for consistent styling.
