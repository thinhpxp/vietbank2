<template>
  <svg :class="['svg-icon', sizeClass, customClass]" :width="computedSize" :height="computedSize" viewBox="0 0 24 24"
    fill="none" xmlns="http://www.w3.org/2000/svg" :stroke="stroke" :stroke-width="strokeWidth" stroke-linecap="round"
    stroke-linejoin="round">
    <component :is="iconComponent" />
  </svg>
</template>

<script>
import { defineComponent, computed, h } from 'vue';

// Icon path definitions
const icons = {
  user: () => h('g', [
    h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
    h('circle', { cx: '12', cy: '7', r: '4' })
  ]),

  logout: () => h('g', [
    h('path', { d: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4' }),
    h('polyline', { points: '16 17 21 12 16 7' }),
    h('line', { x1: '21', y1: '12', x2: '9', y2: '12' })
  ]),

  settings: () => h('g', [
    h('circle', { cx: '12', cy: '12', r: '3' }),
    h('path', { d: 'M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24' })
  ]),

  shield: () => h('path', { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z' }),

  edit: () => h('g', [
    h('path', { d: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7' }),
    h('path', { d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z' })
  ]),

  trash: () => h('g', [
    h('polyline', { points: '3 6 5 6 21 6' }),
    h('path', { d: 'M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2' }),
    h('line', { x1: '10', y1: '11', x2: '10', y2: '17' }),
    h('line', { x1: '14', y1: '11', x2: '14', y2: '17' })
  ]),

  save: () => h('g', [
    h('path', { d: 'M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z' }),
    h('polyline', { points: '17 21 17 13 7 13 7 21' }),
    h('polyline', { points: '7 3 7 8 15 8' })
  ]),

  copy: () => h('g', [
    h('rect', { x: '9', y: '9', width: '13', height: '13', rx: '2', ry: '2' }),
    h('path', { d: 'M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1' })
  ]),

  plus: () => h('g', [
    h('line', { x1: '12', y1: '5', x2: '12', y2: '19' }),
    h('line', { x1: '5', y1: '12', x2: '19', y2: '12' })
  ]),

  lock: () => h('g', [
    h('rect', { x: '3', y: '11', width: '18', height: '11', rx: '2', ry: '2' }),
    h('path', { d: 'M7 11V7a5 5 0 0 1 10 0v4' })
  ]),

  unlock: () => h('g', [
    h('rect', { x: '3', y: '11', width: '18', height: '11', rx: '2', ry: '2' }),
    h('path', { d: 'M7 11V7a5 5 0 0 1 9.9-1' })
  ]),

  check: () => h('polyline', { points: '20 6 9 17 4 12' }),

  x: () => h('g', [
    h('line', { x1: '18', y1: '6', x2: '6', y2: '18' }),
    h('line', { x1: '6', y1: '6', x2: '18', y2: '18' })
  ]),

  alert: () => h('g', [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('line', { x1: '12', y1: '8', x2: '12', y2: '12' }),
    h('line', { x1: '12', y1: '16', x2: '12.01', y2: '16' })
  ]),

  info: () => h('g', [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('line', { x1: '12', y1: '16', x2: '12', y2: '12' }),
    h('line', { x1: '12', y1: '8', x2: '12.01', y2: '8' })
  ]),

  users: () => h('g', [
    h('path', { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
    h('circle', { cx: '9', cy: '7', r: '4' }),
    h('path', { d: 'M23 21v-2a4 4 0 0 0-3-3.87' }),
    h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' })
  ]),

  folder: () => h('path', { d: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z' }),

  file: () => h('g', [
    h('path', { d: 'M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z' }),
    h('polyline', { points: '13 2 13 9 20 9' })
  ]),

  search: () => h('g', [
    h('circle', { cx: '11', cy: '11', r: '8' }),
    h('line', { x1: '21', y1: '21', x2: '16.65', y2: '16.65' })
  ]),

  filter: () => h('polygon', { points: '22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3' }),

  download: () => h('g', [
    h('path', { d: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4' }),
    h('polyline', { points: '7 10 12 15 17 10' }),
    h('line', { x1: '12', y1: '15', x2: '12', y2: '3' })
  ]),

  upload: () => h('g', [
    h('path', { d: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4' }),
    h('polyline', { points: '17 8 12 3 7 8' }),
    h('line', { x1: '12', y1: '3', x2: '12', y2: '15' })
  ]),

  eye: () => h('g', [
    h('path', { d: 'M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z' }),
    h('circle', { cx: '12', cy: '12', r: '3' })
  ]),

  'eye-off': () => h('g', [
    h('path', { d: 'M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24' }),
    h('line', { x1: '1', y1: '1', x2: '23', y2: '23' })
  ]),

  menu: () => h('g', [
    h('line', { x1: '3', y1: '12', x2: '21', y2: '12' }),
    h('line', { x1: '3', y1: '6', x2: '21', y2: '6' }),
    h('line', { x1: '3', y1: '18', x2: '21', y2: '18' })
  ]),

  'chevron-down': () => h('polyline', { points: '6 9 12 15 18 9' }),
  'chevron-up': () => h('polyline', { points: '18 15 12 9 6 15' }),
  'chevron-left': () => h('polyline', { points: '15 18 9 12 15 6' }),
  'chevron-right': () => h('polyline', { points: '9 18 15 12 9 6' }),

  calendar: () => h('g', [
    h('rect', { x: '3', y: '4', width: '18', height: '18', rx: '2', ry: '2' }),
    h('line', { x1: '16', y1: '2', x2: '16', y2: '6' }),
    h('line', { x1: '8', y1: '2', x2: '8', y2: '6' }),
    h('line', { x1: '3', y1: '10', x2: '21', y2: '10' })
  ]),
};

export default defineComponent({
  name: 'SvgIcon',
  props: {
    name: {
      type: String,
      required: true,
      validator: (value) => Object.keys(icons).includes(value)
    },
    size: {
      type: [String, Number],
      default: 'md'
    },
    stroke: {
      type: String,
      default: 'currentColor'
    },
    strokeWidth: {
      type: [String, Number],
      default: 2
    },
    customClass: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const sizeMap = {
      xs: 14,
      sm: 16,
      md: 20,
      lg: 24,
      xl: 32
    };

    const computedSize = computed(() => {
      if (typeof props.size === 'number') return props.size;
      return sizeMap[props.size] || sizeMap.md;
    });

    const sizeClass = computed(() => {
      if (typeof props.size === 'string' && sizeMap[props.size]) {
        return `icon-${props.size}`;
      }
      return '';
    });

    const iconComponent = computed(() => {
      const iconFn = icons[props.name];
      return iconFn ? iconFn() : null;
    });

    return {
      computedSize,
      sizeClass,
      iconComponent
    };
  }
});
</script>

<style scoped>
.svg-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
