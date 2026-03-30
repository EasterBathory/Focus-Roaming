const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const start = html.indexOf('<script>') + 8;
const end = html.lastIndexOf('</script>');
const script = html.slice(start, end);
try {
  new Function(script);
  console.log('OK: no syntax errors');
} catch(e) {
  console.log('ERROR:', e.message);
  // Find the line
  const lines = script.split('\n');
  const match = e.message.match(/line (\d+)/);
  if(match) {
    const ln = parseInt(match[1]);
    for(let i = Math.max(0,ln-3); i < Math.min(lines.length,ln+2); i++) {
      console.log(`  ${i+1}: ${lines[i]}`);
    }
  }
}
