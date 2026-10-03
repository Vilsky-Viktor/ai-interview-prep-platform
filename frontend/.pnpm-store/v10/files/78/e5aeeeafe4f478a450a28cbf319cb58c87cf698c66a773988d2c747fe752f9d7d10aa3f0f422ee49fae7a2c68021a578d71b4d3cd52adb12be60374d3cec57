import { escapeStringForRegex } from '@sentry/core';
import * as fs from 'fs';
import * as path from 'path';

function prefixLoader(userCode) {
  const { templatePrefix, replacements } = "getOptions" in this ? this.getOptions() : this.query;
  const templatePath = path.resolve(__dirname, `../templates/${templatePrefix}PrefixLoaderTemplate.js`);
  this.addDependency(templatePath);
  let templateCode = fs.readFileSync(templatePath).toString();
  replacements.forEach(([placeholder, value]) => {
    const placeholderRegex = new RegExp(escapeStringForRegex(placeholder), "g");
    templateCode = templateCode.replace(placeholderRegex, value);
  });
  return `${templateCode}
${userCode}`;
}

export { prefixLoader as default };
//# sourceMappingURL=prefixLoader.js.map
