export const SortableTableMixin = {
    data() {
        return {
            sortBy: '',
            sortDesc: false
        };
    },
    methods: {
        /**
         * Handle column header click to toggle sort order.
         * @param {String} column - The column key to sort by.
         * @param {String} defaultSort - Optional default sort column.
         */
        toggleSort(column) {
            if (this.sortBy === column) {
                this.sortDesc = !this.sortDesc;
            } else {
                this.sortBy = column;
                this.sortDesc = false;
            }
        },

        /**
         * Return a sort indicator arrow for the column header.
         * @param {String} column - The column key.
         */
        getSortIcon(column) {
            if (this.sortBy !== column) return '';
            return this.sortDesc ? '▼' : '▲';
        },

        /**
         * Return the standardized class for sortable headers.
         * Usage: :class="getSortableClass('id')"
         */
        getSortableClass() {
            return 'ui-sortable';
        },

        /**
         * Sort an array based on current sortBy/sortDesc state.
         * @param {Array} items - The array to sort.
         * @param {Object} mapping - Optional mapping for special fields (e.g. { 'group': 'group_name' }).
         * @returns {Array} Sorted new array.
         */
        sortArray(items, mapping = {}) {
            if (!items || !items.length) return [];

            // Create a shallow copy to avoid mutating original
            const sorted = [...items];

            if (!this.sortBy) return sorted;

            // Determine the actual property key to sort by
            const key = mapping[this.sortBy] || this.sortBy;

            return sorted.sort((a, b) => {
                let valA = a[key];
                let valB = b[key];

                // Null safety
                if (valA === null || valA === undefined) valA = '';
                if (valB === null || valB === undefined) valB = '';

                // Strings case-insensitive check
                if (typeof valA === 'string') valA = valA.toLowerCase();
                if (typeof valB === 'string') valB = valB.toLowerCase();

                if (valA < valB) return this.sortDesc ? 1 : -1;
                if (valA > valB) return this.sortDesc ? -1 : 1;
                return 0;
            });
        }
    }
};
