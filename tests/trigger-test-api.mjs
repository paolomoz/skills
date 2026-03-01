#!/usr/bin/env node

// Skill Trigger Test — AWS Bedrock edition
// Tests whether natural-language prompts cause the model to invoke the Skill tool.
//
// Usage:
//   node tests/trigger-test-api.mjs                         # Run all (loads .env from playground)
//   node tests/trigger-test-api.mjs --skill sse-streaming   # Test one skill
//   node tests/trigger-test-api.mjs --dry-run               # Show prompts without calling API
//   node tests/trigger-test-api.mjs --verbose               # Show response details
//   node tests/trigger-test-api.mjs --model global.anthropic.claude-sonnet-4-5-v1

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROMPTS_FILE = join(__dirname, 'trigger-prompts.json');
const RESULTS_DIR = join(__dirname, 'results');
const REPORT_FILE = join(RESULTS_DIR, 'trigger-report.md');
const RESULTS_JSON = join(RESULTS_DIR, 'trigger-results.json');

// --- Load .env file ---
function loadEnv(filePath) {
  if (!existsSync(filePath)) return;
  const lines = readFileSync(filePath, 'utf-8').split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIdx = trimmed.indexOf('=');
    if (eqIdx === -1) continue;
    const key = trimmed.slice(0, eqIdx);
    let value = trimmed.slice(eqIdx + 1);
    // Strip surrounding quotes
    if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (!process.env[key]) {
      process.env[key] = value;
    }
  }
}

// Load from multiple possible locations (first found wins for each var)
const ENV_PATHS = [
  join(__dirname, '..', '.env'),                          // project root
  '/Users/paolo/playground/playground/.env',               // known location
  '/Users/paolo/playground/tellmenow/.env',                // model config
];
for (const p of ENV_PATHS) loadEnv(p);

// --- Parse CLI args ---
const args = process.argv.slice(2);
function getArg(name) {
  const i = args.indexOf(name);
  return i !== -1 ? args[i + 1] : null;
}
const filterSkill = getArg('--skill');
const dryRun = args.includes('--dry-run');
const verbose = args.includes('--verbose');
const model = getArg('--model') || process.env.ANTHROPIC_MODEL || 'global.anthropic.claude-opus-4-6-v1';
const concurrency = parseInt(getArg('--concurrency') || '3', 10);
const awsRegion = process.env.AWS_REGION || 'us-east-1';
const bearerToken = process.env.ANTHROPIC_AWS_BEARER_TOKEN_BEDROCK;

// --- Load prompts ---
const data = JSON.parse(readFileSync(PROMPTS_FILE, 'utf-8'));
const { skills, negative } = data;

// --- Build the system prompt (mimics Claude Code's skill list) ---
function buildSystemPrompt() {
  let prompt = `You are Claude Code, an AI assistant for software engineering tasks. You have access to tools including a Skill tool for invoking specialized skills.\n\n`;
  prompt += `The following skills are available for use with the Skill tool:\n\n`;
  for (const [name, info] of Object.entries(skills)) {
    prompt += `- ${name}: ${info.description}\n`;
  }
  prompt += `\nWhen a user's request matches a skill, use the Skill tool to invoke it. Only invoke a skill if the request clearly matches its purpose. Do not invoke skills for generic programming questions.`;
  return prompt;
}

// --- Skill tool definition (matches Claude Code's schema) ---
const SKILL_TOOL = {
  name: 'Skill',
  description: 'Execute a skill within the main conversation. Use this tool when the user\'s request matches an available skill.',
  input_schema: {
    type: 'object',
    properties: {
      skill: { type: 'string', description: 'The skill name to invoke' },
      args: { type: 'string', description: 'Optional arguments for the skill' },
    },
    required: ['skill'],
  },
};

// --- Build test cases ---
const testCases = [];
for (const [skillName, info] of Object.entries(skills)) {
  if (filterSkill && skillName !== filterSkill) continue;
  for (const prompt of info.prompts) {
    testCases.push({
      skill: skillName,
      prompt,
      expected: skillName,
      signals: info.signals || [],
    });
  }
}
if (!filterSkill) {
  for (const prompt of negative) {
    testCases.push({
      skill: '__negative__',
      prompt,
      expected: '__none__',
      signals: [],
    });
  }
}

console.log(`=== Skill Trigger Test (Bedrock) ===`);
console.log(`Model:  ${model}`);
console.log(`Region: ${awsRegion}`);
console.log(`Tests:  ${testCases.length} | Concurrency: ${concurrency}`);
console.log(``);

if (dryRun) {
  let current = '';
  for (const tc of testCases) {
    if (tc.skill !== current) {
      current = tc.skill;
      console.log(`[${current}]`);
    }
    console.log(`  > ${tc.prompt}`);
    console.log(`    expected: ${tc.expected}`);
  }
  console.log(`\nTotal: ${testCases.length} test cases`);
  process.exit(0);
}

// --- Verify credentials ---
if (!bearerToken) {
  console.error('Error: ANTHROPIC_AWS_BEARER_TOKEN_BEDROCK not found.');
  console.error('  Set it in your environment or in .env');
  console.error(`  Searched: ${ENV_PATHS.join(', ')}`);
  process.exit(1);
}
console.log(`Auth:   Bearer token (${bearerToken.slice(0, 8)}...)`);
console.log(``);

mkdirSync(RESULTS_DIR, { recursive: true });
const systemPrompt = buildSystemPrompt();

if (verbose) {
  console.log('--- System prompt ---');
  console.log(systemPrompt.slice(0, 500) + '...');
  console.log('---\n');
}

// --- Bedrock API call ---
async function callAPI(prompt) {
  const encodedModel = encodeURIComponent(model);
  const url = `https://bedrock-runtime.${awsRegion}.amazonaws.com/model/${encodedModel}/invoke`;

  const body = {
    anthropic_version: 'bedrock-2023-05-31',
    max_tokens: 1024,
    system: systemPrompt,
    tools: [SKILL_TOOL],
    messages: [{ role: 'user', content: prompt }],
  };

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${bearerToken}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Bedrock ${res.status}: ${text.slice(0, 300)}`);
  }

  return res.json();
}

// --- Analyze response ---
function analyzeResponse(response, expected, signals) {
  let detectedSkill = null;
  let method = 'none';
  let textContent = '';

  for (const block of response.content || []) {
    if (block.type === 'tool_use' && block.name === 'Skill') {
      method = 'tool_use';
      detectedSkill = block.input?.skill || null;
    }
    if (block.type === 'text') {
      textContent += block.text;
    }
  }

  // Fallback: signal word detection in text
  if (method === 'none' && signals.length > 0) {
    const lower = textContent.toLowerCase();
    for (const signal of signals) {
      if (lower.includes(signal.toLowerCase())) {
        method = 'text_match';
        break;
      }
    }
  }

  // Determine status
  let status;
  if (expected === '__none__') {
    status = (detectedSkill === null && method === 'none') ? 'PASS' : 'FAIL';
  } else if (detectedSkill === expected) {
    status = 'PASS';
  } else if (method === 'text_match') {
    status = 'FALLBACK';
  } else {
    status = 'FAIL';
  }

  const snippet = textContent.slice(0, 120).replace(/\n/g, ' ').trim();

  return { skill: detectedSkill, method, status, snippet };
}

// --- Run tests ---
async function runTest(tc, index) {
  const label = `[${index + 1}/${testCases.length}] ${tc.skill}`;
  process.stdout.write(`${label}: "${tc.prompt.slice(0, 55)}..." `);

  try {
    const response = await callAPI(tc.prompt);
    const analysis = analyzeResponse(response, tc.expected, tc.signals);

    if (verbose) {
      console.log(`\n  Response blocks: ${response.content?.map(b => b.type).join(', ')}`);
      if (analysis.snippet) console.log(`  Snippet: ${analysis.snippet.slice(0, 80)}`);
    }

    const result = {
      skill: tc.skill,
      prompt: tc.prompt,
      expected: tc.expected,
      detected: analysis.skill || 'none',
      method: analysis.method,
      status: analysis.status,
      snippet: analysis.snippet,
    };

    console.log(analysis.status === 'PASS' ? 'PASS' :
      analysis.status === 'FALLBACK' ? 'FALLBACK' :
      `**FAIL** (got: ${analysis.skill || 'none'})`);
    return result;
  } catch (err) {
    console.log(`ERROR: ${err.message.slice(0, 120)}`);
    return {
      skill: tc.skill,
      prompt: tc.prompt,
      expected: tc.expected,
      detected: 'none',
      method: 'none',
      status: 'ERROR',
      snippet: err.message.slice(0, 120),
    };
  }
}

// Batch with concurrency limit
async function runAll() {
  const allResults = new Array(testCases.length);

  for (let i = 0; i < testCases.length; i += concurrency) {
    const batch = testCases.slice(i, i + concurrency);
    const batchResults = await Promise.all(
      batch.map((tc, j) => runTest(tc, i + j))
    );
    batchResults.forEach((r, j) => {
      allResults[i + j] = r;
    });

    // Small delay between batches to avoid rate limits
    if (i + concurrency < testCases.length) {
      await new Promise(r => setTimeout(r, 500));
    }
  }

  return allResults;
}

const allResults = await runAll();

// --- Tally ---
let pass = 0, fallback = 0, fail = 0, negPass = 0, negTotal = 0;
for (const r of allResults) {
  if (r.expected === '__none__') {
    negTotal++;
    if (r.status === 'PASS') negPass++;
    else fail++;
  } else if (r.status === 'PASS') {
    pass++;
  } else if (r.status === 'FALLBACK') {
    fallback++;
  } else {
    fail++;
  }
}

// --- Write JSON results ---
writeFileSync(RESULTS_JSON, JSON.stringify(allResults, null, 2));

// --- Generate markdown report ---
const timestamp = new Date().toISOString();
let md = `# Skill Trigger Test Report\nGenerated: ${timestamp}\nModel: ${model}\n\n`;
md += `## Summary\n`;
md += `- Total: ${allResults.length} | Pass: ${pass} | Fallback: ${fallback} | Fail: ${fail}\n`;
if (negTotal > 0) md += `- Negative (no trigger): ${negPass}/${negTotal}\n`;
md += `\n## Results\n\n`;
md += `| # | Skill | Prompt | Expected | Detected | Method | Status |\n`;
md += `|---|-------|--------|----------|----------|--------|--------|\n`;

allResults.forEach((r, i) => {
  const prompt = r.prompt.length > 50 ? r.prompt.slice(0, 47) + '...' : r.prompt;
  const badge = r.status === 'FAIL' || r.status === 'ERROR' ? `**${r.status}**` : r.status;
  md += `| ${i + 1} | ${r.skill} | "${prompt}" | ${r.expected} | ${r.detected} | ${r.method} | ${badge} |\n`;
});

// Failed tests detail
const failures = allResults.filter(r => r.status === 'FAIL' || r.status === 'ERROR');
md += `\n## Failed Tests\n\n`;
if (failures.length === 0) {
  md += `No failures.\n`;
} else {
  for (const f of failures) {
    md += `### ${f.skill}\n`;
    md += `- **Prompt**: "${f.prompt}"\n`;
    md += `- **Expected**: ${f.expected}\n`;
    md += `- **Detected**: ${f.detected}\n`;
    md += `- **Snippet**: ${f.snippet}\n\n`;
  }
}

writeFileSync(REPORT_FILE, md);

// --- Summary ---
console.log(`\n=========================================`);
console.log(`DONE`);
console.log(`  Pass: ${pass} | Fallback: ${fallback} | Fail: ${fail}`);
if (negTotal > 0) console.log(`  Negative: ${negPass}/${negTotal}`);
console.log(``);
console.log(`Report:  ${REPORT_FILE}`);
console.log(`Data:    ${RESULTS_JSON}`);
