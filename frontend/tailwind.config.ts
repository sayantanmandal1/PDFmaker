import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: {
          primary: '#0a0a0a',
          secondary: '#1a1a1a',
          glass: 'rgba(255, 255, 255, 0.05)',
        },
        accent: {
          red: {
            light: '#ef4444',
            DEFAULT: '#dc2626',
            dark: '#b91c1c',
          },
          yellow: {
            light: '#fbbf24',
            DEFAULT: '#f59e0b',
            dark: '#d97706',
          },
        },
        text: {
          primary: '#ffffff',
          secondary: '#d1d5db',
          muted: '#9ca3af',
        },
        status: {
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6',
        },
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '12px',
        lg: '16px',
        xl: '24px',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #ef4444 0%, #f59e0b 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
        'gradient-accent': 'linear-gradient(135deg, #dc2626 0%, transparent 100%)',
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },
      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },
      transitionDuration: {
        '200': '200ms',
        '300': '300ms',
      },
    },
  },
  plugins: [],
}
export default config