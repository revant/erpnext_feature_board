const fs = require('fs-extra');
const concat = require('concat');

(async function build() {
  const files = [
    './dist/webcomponents/runtime.js',
    './dist/webcomponents/polyfills.js',
    './dist/webcomponents/main.js',
  ];

  await fs.ensureDir('elements');
  await concat(files, 'elements/webcomponents.js');
  await concat(['./dist/webcomponents/styles.css'], 'elements/webcomponents.css')
})();
