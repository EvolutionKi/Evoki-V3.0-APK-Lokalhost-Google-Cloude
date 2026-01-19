export type DisplayMode = 'mobile' | 'tablet' | 'desktop';

export interface DisplaySettings {
    mode: DisplayMode;
    fontSize: {
        base: string;
        sm: string;
        lg: string;
        xl: string;
    };
    spacing: {
        xs: string;
        sm: string;
        md: string;
        lg: string;
        xl: string;
    };
    maxWidth: string;
    compactMode: boolean;
}

export const DISPLAY_MODES: Record<DisplayMode, DisplaySettings> = {
    mobile: {
        mode: 'mobile',
        fontSize: {
            base: '14px',
            sm: '12px',
            lg: '16px',
            xl: '20px',
        },
        spacing: {
            xs: '0.25rem',
            sm: '0.5rem',
            md: '0.75rem',
            lg: '1rem',
            xl: '1.5rem',
        },
        maxWidth: '100%',
        compactMode: true,
    },
    tablet: {
        mode: 'tablet',
        fontSize: {
            base: '15px',
            sm: '13px',
            lg: '17px',
            xl: '22px',
        },
        spacing: {
            xs: '0.375rem',
            sm: '0.75rem',
            md: '1rem',
            lg: '1.5rem',
            xl: '2rem',
        },
        maxWidth: '1024px',
        compactMode: false,
    },
    desktop: {
        mode: 'desktop',
        fontSize: {
            base: '16px',
            sm: '14px',
            lg: '18px',
            xl: '24px',
        },
        spacing: {
            xs: '0.5rem',
            sm: '1rem',
            md: '1.25rem',
            lg: '2rem',
            xl: '3rem',
        },
        maxWidth: '1440px',
        compactMode: false,
    },
};

export const DEFAULT_DISPLAY_MODE: DisplayMode = 'desktop';
