Object.defineProperties(exports, { __esModule: { value: true }, [Symbol.toStringTag]: { value: 'Module' } });

const core = require('@sentry/core');
const fs = require('fs');
const path = require('path');

function prefixLoader(userCode) {
  const { templatePrefix, replacements } = "getOptions" in this ? this.getOptions() : this.query;
  const templatePath = path.resolve(__dirname, `../templates/${templatePrefix}PrefixLoaderTemplate.js`);
  this.addDependency(templatePath);
  let templateCode = fs.readFileSync(templatePath).toString();
  replacements.forEach(([placeholder, value]) => {
    const placeholderRegex = new RegExp(core.escapeStringForRegex(placeholder), "g");
    templateCode = templateCode.replace(placeholderRegex, value);
  });
  return `${templateCode}
${userCode}`;
}

exports.default = prefixLoader;
//# sourceMappingURL=prefixLoader.js.map
