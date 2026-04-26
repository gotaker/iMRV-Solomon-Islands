module.exports = {
  presets: [require('frappe-ui/tailwind')],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/frappe/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        forest: '#01472e',
        sage: '#ccd5ae',
        olive: '#e9edc9',
        cream: '#fefae0',
        moss: '#a3b18a',
      },
      fontFamily: {
        display: ['Anton', 'Helvetica Neue', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      transitionTimingFunction: {
        editorial: 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      boxShadow: {
        forest: '0 25px 60px -25px rgba(1, 71, 46, 0.2)',
        'forest-lg': '0 30px 80px -20px rgba(1, 71, 46, 0.2)',
      },
    },
  },
  plugins: [],
}
