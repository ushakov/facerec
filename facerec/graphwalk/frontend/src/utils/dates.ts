/**
 * Format a date string (YYYY-MM-DD) into a human-readable format
 */
export const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'Unknown date';

    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
};

/**
 * Group timeline faces by year and month
 */
export const groupTimelineFaces = <T extends { image_date: string | null }>(
    faces: T[]
): Record<string, Record<string, T[]>> => {
    const grouped: Record<string, Record<string, T[]>> = {};

    faces.forEach(face => {
        if (!face.image_date) {
            const year = 'Unknown';
            const month = 'Unknown';
            grouped[year] = grouped[year] || {};
            grouped[year][month] = grouped[year][month] || [];
            grouped[year][month].push(face);
            return;
        }

        const date = new Date(face.image_date);
        const year = date.getFullYear().toString();
        const month = date.toLocaleString('en-US', { month: 'long' });

        grouped[year] = grouped[year] || {};
        grouped[year][month] = grouped[year][month] || [];
        grouped[year][month].push(face);
    });

    return grouped;
};

/**
 * Get a short formatted date (e.g. "Jan 15, 2024")
 */
export const formatShortDate = (dateStr: string | null): string => {
    if (!dateStr) return 'Unknown';

    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
};

/**
 * Sort dates in ascending or descending order, handling null dates
 */
export const sortDates = (a: string | null, b: string | null, order: 'asc' | 'desc' = 'desc'): number => {
    if (a === null && b === null) return 0;
    if (a === null) return order === 'asc' ? 1 : -1;
    if (b === null) return order === 'asc' ? -1 : 1;

    const dateA = new Date(a);
    const dateB = new Date(b);

    return order === 'asc'
        ? dateA.getTime() - dateB.getTime()
        : dateB.getTime() - dateA.getTime();
};