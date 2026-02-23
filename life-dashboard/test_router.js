const fs = require('fs');
let code = fs.readFileSync('schedule_data.js', 'utf8');
eval(code);

const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
for (let i = 0; i < 7; i++) {
    global.Date.prototype.getDay = () => i;
    console.log(`\n\n=== ${days[i]} ===`);
    let timeline = window.generateTodayTimeline();
    timeline.forEach(t => console.log(`${t.time} | ${t.title} [${t.tags.join(',')}]`));
}
