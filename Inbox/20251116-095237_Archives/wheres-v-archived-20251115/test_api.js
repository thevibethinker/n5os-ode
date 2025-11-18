const resp1 = await fetch('http://localhost:54179/api/status');
const data = await resp1.json();
console.log('API Status:', data.hasTrip ? '✓ Working' : '✗ Failed');

const resp2 = await fetch('http://localhost:54179/');
const html = await resp2.text();
console.log('HTML:', html.includes('root') ? '✓ Loads' : '✗ Failed');
console.log('Scripts:', html.includes('main.tsx') ? '✓ Present' : '✗ Missing');
