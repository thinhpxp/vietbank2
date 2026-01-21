
export const FilterableTableMixin = {
    methods: {
        /**
         * Filter an array based on a configuration schema.
         * 
         * @param {Array} items - The source array to filter.
         * @param {Object} filters - The current filter values (e.g. { search: 'abc', group: 1 }).
         * @param {Object} config - The schema defining how to filter each key.
         * 
         * Config Schema Example:
         * {
         *   search: { type: 'text', fields: ['name', 'code'] },
         *   status: { type: 'exact' }, // assumes field='status'
         *   role: { type: 'exact', field: 'role_id' },
         *   tags: { type: 'array_includes', field: 'tag_ids' }
         * }
         */
        filterArray(items, filters, config) {
            if (!items || !items.length) return [];

            return items.filter(item => {
                for (const [filterKey, filterConfig] of Object.entries(config)) {
                    const filterValue = filters[filterKey];

                    // Skip empty filters (null, undefined, empty string)
                    if (filterValue === null || filterValue === undefined || filterValue === '') {
                        continue;
                    }

                    const type = filterConfig.type || 'exact';

                    // 1. Text Search (Partial Match)
                    if (type === 'text') {
                        const searchStr = String(filterValue).toLowerCase();
                        // Priority: config.fields (array) > config.field (string) > filterKey
                        const fields = filterConfig.fields || (filterConfig.field ? [filterConfig.field] : [filterKey]);

                        const hasMatch = fields.some(f => {
                            const val = item[f];
                            return val && String(val).toLowerCase().includes(searchStr);
                        });

                        if (!hasMatch) return false;
                    }

                    // 2. Exact Match
                    else if (type === 'exact') {
                        const field = filterConfig.field || filterKey;
                        if (item[field] != filterValue) return false;
                    }

                    // 3. Array Includes
                    else if (type === 'array_includes') {
                        const field = filterConfig.field || filterKey;
                        const list = item[field];
                        if (!Array.isArray(list) || !list.includes(filterValue)) return false;
                    }

                    // 4. Date Match (YYYY-MM-DD)
                    else if (type === 'date') {
                        const field = filterConfig.field || filterKey;
                        const itemVal = item[field];
                        if (!itemVal) return false;

                        const datePart = new Date(itemVal).toISOString().split('T')[0];
                        if (datePart !== filterValue) return false;
                    }
                }

                return true;
            });
        }
    }
};
