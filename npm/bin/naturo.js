#!/usr/bin/env node

/**
 * Naturo npm wrapper — delegates to the Python `naturo` CLI.
 *
 * Usage:
 *   npx naturo mcp start          # Start MCP server (stdio)
 *   npx naturo capture live       # Take a screenshot
 *   npx naturo --help             # Full CLI help
 *
 * Requires Python 3.9+ and `pip install naturo` (or naturo on PATH).
 */

"use strict";

const { spawn } = require("child_process");
const { execSync } = require("child_process");

const args = process.argv.slice(2);

/**
 * Find the naturo CLI executable. Tries:
 *   1. `naturo` on PATH (pip-installed)
 *   2. `python -m naturo` as module
 *   3. `python3 -m naturo` as module
 */
function findNaturo() {
  // Try naturo on PATH
  try {
    execSync("naturo --version", { stdio: "ignore" });
    return { cmd: "naturo", args: [] };
  } catch {
    // not on PATH
  }

  // Try python -m naturo
  for (const py of ["python", "python3"]) {
    try {
      execSync(`${py} -m naturo --version`, { stdio: "ignore" });
      return { cmd: py, args: ["-m", "naturo"] };
    } catch {
      // try next
    }
  }

  return null;
}

function printInstallHelp() {
  console.error(
    "Error: naturo Python package not found.\n" +
      "\n" +
      "Install it with:\n" +
      "  pip install naturo\n" +
      "\n" +
      "Requires Python 3.9+. See https://github.com/AcePeak/naturo"
  );
  process.exit(1);
}

const naturo = findNaturo();
if (!naturo) {
  printInstallHelp();
}

const child = spawn(naturo.cmd, [...naturo.args, ...args], {
  stdio: "inherit",
  windowsHide: false,
});

child.on("error", (err) => {
  if (err.code === "ENOENT") {
    printInstallHelp();
  } else {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
  } else {
    process.exit(code ?? 1);
  }
});
