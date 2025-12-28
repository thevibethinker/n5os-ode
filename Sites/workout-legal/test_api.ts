const port = 58630;
const resp = await fetch(`http://localhost:${port}/api/health/summary`);
console.log(JSON.stringify(await resp.json(), null, 2));
