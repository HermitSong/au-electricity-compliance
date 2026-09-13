/* Legacy automatic browser recovery is intentionally disabled in this edition. */
'use strict';
process.stderr.write(
  'Automatic browser recovery is disabled: no browser will be launched.\n' +
  'Use skills/au-lawful-source-acquisition/SKILL.md and the permission-gated ' +
  'collect_source_originals.py workflow. If a permitted source needs rendering, ' +
  'review access and reproduction rights before a separate manual browser capture.\n'
);
process.exitCode = 2;
