/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/*.py',
    './apps/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // NextStepConsulting colors
        marine: '#071D59',
        gold: '#F2B21B',
        light: '#F5F7FA', nsBlue: '#1767D3',
        // Visanextstep (Old CampusVisa) colors
        visaBlue: '#0055A4',
        visaRed: '#EF4135',
        accent: '#EF4135', // For backward compatibility in dashboard
        secondary: '#0055A4', // For backward compatibility
      },
      keyframes: { marquee: { "0%": { transform: "translateX(0%)" }, "100%": { transform: "translateX(-100%)" } }, float: { "0%, 100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-20px)" } }, fadeInUp: { "0%": { opacity: "0", transform: "translateY(20px)" }, "100%": { opacity: "1", transform: "translateY(0)" } } }, animation: { marquee: "marquee 25s linear infinite", float: "float 6s ease-in-out infinite", "fade-in-up": "fadeInUp 1s ease-out forwards" }, fontFamily: {
        satoshi: ['Satoshi', 'sans-serif'],
      },
    },
  },
  plugins: [],
}





