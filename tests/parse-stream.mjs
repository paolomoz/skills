#!/usr/bin/env node

// Parse claude --output-format stream-json from stdin
// Detect whether a Skill tool was invoked and which skill was triggered
//
// Usage:
//   claude -p --output-format stream-json "prompt" | node tests/parse-stream.mjs --expected "skill-name"
//   echo '...' | node tests/parse-stream.mjs --signals "word1,word2"

import { createInterface } from 'readline';

const args = process.argv.slice(2);
const expectedIndex = args.indexOf('--expected');
const expectedSkill = expectedIndex !== -1 ? args[expectedIndex + 1] : null;

const signalsIndex = args.indexOf('--signals');
const signals = signalsIndex !== -1 ? args[signalsIndex + 1].split(',') : [];

const rl = createInterface({ input: process.stdin });

let detectedSkill = null;
let detectionMethod = 'none';
let textContent = '';
let textSnippet = '';

for await (const line of rl) {
  if (!line.trim()) continue;

  let event;
  try {
    event = JSON.parse(line);
  } catch {
    continue; // skip non-JSON lines
  }

  // Collect assistant text for signal-word fallback
  if (event.type === 'content_block_delta' && event.delta?.type === 'text_delta') {
    textContent += event.delta.text || '';
  }

  // Also handle the "result" wrapper that claude CLI emits
  if (event.type === 'result' && typeof event.result === 'string') {
    textContent += event.result;
  }
  if (event.type === 'message' && event.message?.content) {
    for (const block of event.message.content) {
      if (block.type === 'text') textContent += block.text;
    }
  }

  // Primary detection: look for Skill tool_use
  if (event.type === 'content_block_start' && event.content_block?.type === 'tool_use') {
    const toolName = event.content_block.name;
    if (toolName === 'Skill') {
      // The skill name may appear in partial JSON in subsequent deltas
      // Mark that we found a Skill call — we'll extract the name from accumulated input
      detectionMethod = 'tool_use';
    }
  }

  // tool_use input arrives as input_json_delta events
  if (event.type === 'content_block_delta' && event.delta?.type === 'input_json_delta') {
    if (detectionMethod === 'tool_use' && !detectedSkill) {
      // Accumulate partial JSON and try to extract skill name
      const partial = event.delta.partial_json || '';
      const skillMatch = partial.match(/"skill"\s*:\s*"([^"]+)"/);
      if (skillMatch) {
        detectedSkill = skillMatch[1];
      }
    }
  }

  // Also check for complete tool_use blocks in message content
  if (event.type === 'message' && event.message?.content) {
    for (const block of event.message.content) {
      if (block.type === 'tool_use' && block.name === 'Skill') {
        detectionMethod = 'tool_use';
        if (block.input?.skill) {
          detectedSkill = block.input.skill;
        }
      }
    }
  }

  // Handle the "result" event that claude CLI may emit with tool calls
  if (event.type === 'result' && event.tool_use) {
    if (event.tool_use.name === 'Skill') {
      detectionMethod = 'tool_use';
      if (event.tool_use.input?.skill) {
        detectedSkill = event.tool_use.input.skill;
      }
    }
  }
}

// If tool_use was detected but we couldn't parse the skill name from deltas,
// try to find it in the full accumulated text (sometimes the JSON appears there)
if (detectionMethod === 'tool_use' && !detectedSkill) {
  const match = textContent.match(/["']skill["']\s*:\s*["']([^"']+)["']/);
  if (match) detectedSkill = match[1];
}

// Fallback: check text content for signal words
if (detectionMethod === 'none' && signals.length > 0) {
  const lowerText = textContent.toLowerCase();
  for (const signal of signals) {
    if (lowerText.includes(signal.toLowerCase())) {
      detectionMethod = 'text_match';
      textSnippet = signal;
      break;
    }
  }
}

// Build a short snippet from the response for the report
if (!textSnippet && textContent.length > 0) {
  textSnippet = textContent.slice(0, 120).replace(/\n/g, ' ').trim();
  if (textContent.length > 120) textSnippet += '...';
}

const result = {
  skill: detectedSkill,
  method: detectionMethod,
  text_snippet: textSnippet,
};

// Determine pass/fail if --expected was given
if (expectedSkill !== null) {
  if (expectedSkill === '__none__') {
    // Negative test: should NOT trigger any skill
    result.pass = detectedSkill === null && detectionMethod === 'none';
    result.status = result.pass ? 'PASS' : 'FAIL';
  } else {
    if (detectedSkill === expectedSkill) {
      result.pass = true;
      result.status = 'PASS';
    } else if (detectionMethod === 'text_match') {
      result.pass = true;
      result.status = 'FALLBACK';
    } else {
      result.pass = false;
      result.status = 'FAIL';
    }
  }
}

console.log(JSON.stringify(result));
