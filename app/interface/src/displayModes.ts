// Display Modes - Step 1.1 & 1.2: Config with 3 Responsive Modes

export interface DisplayMode {
    name: string;
    fontSize: {
        base: string;      // Body text
        heading: string;   // H1, H2, etc.
        small: string;     // Small text, captions
    };
    spacing: {
        sm: string;        // Small gaps
        md: string;        // Medium padding
        lg: string;        // Large spacing
    };
    container: {
        maxWidth: string;  // Max container width
    };
    iconSize: {
        sm: string;        // Small icons
        md: string;        // Medium icons
        lg: string;        // Large icons
    };
}

// Step 1.2: 3 Display Modes
export const DISPLAY_MODES: Record<string, DisplayMode> = {
    mobile: {
        name: 'Mobile 📱',
        fontSize: {
            base: '14px',
            heading: '20px',
            small: '12px',
        },
        spacing: {
            sm: '8px',
            md: '12px',
            lg: '16px',
        },
        container: {
            maxWidth: '100%',
        },
        iconSize: {
            sm: '16px',
            md: '20px',
            lg: '24px',
        },
    },
    tablet: {
        name: 'Tablet 📱💻',
        fontSize: {
            base: '16px',
            heading: '24px',
            small: '14px',
        },
        spacing: {
            sm: '12px',
            md: '16px',
            lg: '24px',
        },
        container: {
            maxWidth: '768px',
        },
        iconSize: {
            sm: '20px',
            md: '24px',
            lg: '32px',
        },
    },
    desktop: {
        name: 'Desktop 💻',
        fontSize: {
            base: '18px',
            heading: '28px',
            small: '16px',
        },
        spacing: {
            sm: '16px',
            md: '20px',
            lg: '32px',
        },
        container: {
            maxWidth: '1200px',
        },
        iconSize: {
            sm: '24px',
            md: '28px',
            lg: '36px',
        },
    },
};

export const DEFAULT_DISPLAY_MODE = 'desktop';
