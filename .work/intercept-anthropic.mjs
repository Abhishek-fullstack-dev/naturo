/**
 * Intercept OpenClaw/pi-ai's actual Anthropic API requests.
 * Hooks both fetch and https.request at the lowest level.
 * Outputs full request/response pairs to a log file.
 */
import { createRequire } from 'module';
import https from 'https';
import http from 'http';
import fs from 'fs';

const require = createRequire(import.meta.url);
const LOG_FILE = '/Users/ace/Ace/naturo/.work/anthropic-requests.log';

// Clear log
fs.writeFileSync(LOG_FILE, `=== Anthropic Request Intercept Log ===\nStarted: ${new Date().toISOString()}\n\n`);

function log(msg) {
    fs.appendFileSync(LOG_FILE, msg + '\n');
    console.log(msg);
}

// ── Hook 1: Monkey-patch globalThis.fetch ──
const origFetch = globalThis.fetch;
let reqCounter = 0;

globalThis.fetch = async function(input, init) {
    const url = typeof input === 'string' ? input : input?.url || String(input);
    
    if (!url.includes('anthropic') && !url.includes('claude')) {
        return origFetch(input, init);
    }
    
    const id = ++reqCounter;
    log(`\n${'='.repeat(80)}`);
    log(`REQUEST #${id} — ${new Date().toISOString()}`);
    log(`${'='.repeat(80)}`);
    log(`URL: ${url}`);
    log(`Method: ${init?.method || 'GET'}`);
    
    // Extract headers
    log(`\nHeaders:`);
    if (init?.headers) {
        let entries;
        if (init.headers instanceof Headers) {
            entries = [...init.headers.entries()];
        } else if (Array.isArray(init.headers)) {
            entries = init.headers;
        } else {
            entries = Object.entries(init.headers);
        }
        for (const [k, v] of entries) {
            // Mask tokens but show format
            const val = String(v);
            if (k.toLowerCase() === 'authorization' || k.toLowerCase() === 'x-api-key') {
                log(`  ${k}: ${val.slice(0, 30)}...${val.slice(-10)} (len=${val.length})`);
            } else {
                log(`  ${k}: ${val}`);
            }
        }
    }
    
    // Log body
    if (init?.body) {
        const bodyStr = typeof init.body === 'string' ? init.body : init.body.toString();
        try {
            const parsed = JSON.parse(bodyStr);
            log(`\nBody (formatted):\n${JSON.stringify(parsed, null, 2)}`);
        } catch {
            log(`\nBody (raw): ${bodyStr.slice(0, 2000)}`);
        }
    }
    
    // Make actual request
    const resp = await origFetch(input, init);
    const cloned = resp.clone();
    
    log(`\n${'─'.repeat(40)}`);
    log(`RESPONSE #${id}`);
    log(`${'─'.repeat(40)}`);
    log(`Status: ${resp.status} ${resp.statusText}`);
    
    // Log response headers
    log(`\nResponse Headers:`);
    resp.headers.forEach((v, k) => log(`  ${k}: ${v}`));
    
    // Log response body
    try {
        const text = await cloned.text();
        try {
            const parsed = JSON.parse(text);
            // Truncate content for readability
            const display = JSON.stringify(parsed, null, 2);
            log(`\nResponse Body:\n${display.slice(0, 3000)}`);
        } catch {
            log(`\nResponse Body (text): ${text.slice(0, 3000)}`);
        }
    } catch (e) {
        log(`\nResponse Body: [failed to read: ${e.message}]`);
    }
    
    log(`\n${'='.repeat(80)}\n`);
    
    return resp;
};

// ── Now make an API call using pi-ai's anthropic provider ──
log('\n>>> Loading pi-ai anthropic provider...');

try {
    // Read credentials the same way OpenClaw does
    const Anthropic = require('/usr/local/lib/node_modules/openclaw/node_modules/@anthropic-ai/sdk');
    const Client = Anthropic.default || Anthropic;
    
    // Read from keychain (like OpenClaw does)
    const { execSync } = await import('child_process');
    const keychainData = JSON.parse(execSync('security find-generic-password -s "Claude Code-credentials" -w', { encoding: 'utf-8' }).trim());
    const oauth = keychainData.claudeAiOauth;
    
    log(`\n>>> Keychain OAuth data:`);
    log(`  accessToken prefix: ${oauth.accessToken?.slice(0, 20)}...`);
    log(`  refreshToken prefix: ${oauth.refreshToken?.slice(0, 20)}...`);
    log(`  expiresAt: ${oauth.expiresAt} (${new Date(oauth.expiresAt).toISOString()})`);
    log(`  scopes: ${JSON.stringify(oauth.scopes)}`);
    log(`  subscriptionType: ${oauth.subscriptionType}`);
    
    // Method 1: Try with accessToken as authToken (Bearer)
    log('\n>>> Method 1: authToken (Bearer) with accessToken from keychain');
    const client1 = new Client({
        apiKey: null,
        authToken: oauth.accessToken,
        dangerouslyAllowBrowser: true,
        defaultHeaders: {
            'accept': 'application/json',
            'anthropic-dangerous-direct-browser-access': 'true',
            'anthropic-beta': 'claude-code-20250219,oauth-2025-04-20',
            'user-agent': 'claude-cli/2.1.75',
            'x-app': 'cli',
        }
    });
    
    try {
        const resp1 = await client1.messages.create({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 20,
            messages: [{ role: 'user', content: 'Say hi in exactly one word' }]
        });
        log(`\n✅ Method 1 SUCCESS: ${resp1.content[0]?.text}`);
    } catch(e) {
        log(`\n❌ Method 1 FAILED: ${e.status} ${e.message?.slice(0, 200)}`);
    }
    
    // Method 2: Try with refreshToken
    log('\n>>> Method 2: authToken (Bearer) with refreshToken from keychain');
    const client2 = new Client({
        apiKey: null,
        authToken: oauth.refreshToken,
        dangerouslyAllowBrowser: true,
        defaultHeaders: {
            'accept': 'application/json',
            'anthropic-dangerous-direct-browser-access': 'true',
            'anthropic-beta': 'claude-code-20250219,oauth-2025-04-20',
            'user-agent': 'claude-cli/2.1.75',
            'x-app': 'cli',
        }
    });
    
    try {
        const resp2 = await client2.messages.create({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 20,
            messages: [{ role: 'user', content: 'Say hi in exactly one word' }]
        });
        log(`\n✅ Method 2 SUCCESS: ${resp2.content[0]?.text}`);
    } catch(e) {
        log(`\n❌ Method 2 FAILED: ${e.status} ${e.message?.slice(0, 200)}`);
    }
    
    // Method 3: Try accessToken as apiKey (x-api-key)
    log('\n>>> Method 3: apiKey (x-api-key) with accessToken');
    const client3 = new Client({
        apiKey: oauth.accessToken,
        dangerouslyAllowBrowser: true,
        defaultHeaders: {
            'accept': 'application/json',
            'anthropic-beta': 'claude-code-20250219,oauth-2025-04-20',
            'user-agent': 'claude-cli/2.1.75',
            'x-app': 'cli',
        }
    });
    
    try {
        const resp3 = await client3.messages.create({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 20,
            messages: [{ role: 'user', content: 'Say hi in exactly one word' }]
        });
        log(`\n✅ Method 3 SUCCESS: ${resp3.content[0]?.text}`);
    } catch(e) {
        log(`\n❌ Method 3 FAILED: ${e.status} ${e.message?.slice(0, 200)}`);
    }

    // Method 4: Try with auth-profiles.json token as apiKey
    log('\n>>> Method 4: apiKey with auth-profiles.json token');
    const authProfiles = JSON.parse(fs.readFileSync('/Users/ace/.openclaw/agents/main/agent/auth-profiles.json', 'utf-8'));
    const profileToken = authProfiles.profiles['anthropic:default'].token;
    log(`  profile token prefix: ${profileToken.slice(0, 20)}...`);
    
    const client4 = new Client({
        apiKey: profileToken,
        dangerouslyAllowBrowser: true,
        defaultHeaders: {
            'accept': 'application/json',
            'anthropic-beta': 'claude-code-20250219,oauth-2025-04-20',
            'user-agent': 'claude-cli/2.1.75',
            'x-app': 'cli',
        }
    });
    
    try {
        const resp4 = await client4.messages.create({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 20,
            messages: [{ role: 'user', content: 'Say hi in exactly one word' }]
        });
        log(`\n✅ Method 4 SUCCESS: ${resp4.content[0]?.text}`);
    } catch(e) {
        log(`\n❌ Method 4 FAILED: ${e.status} ${e.message?.slice(0, 200)}`);
    }

} catch(e) {
    log(`\nFATAL ERROR: ${e.stack || e.message}`);
}

log(`\n\n=== Done. Log written to ${LOG_FILE} ===`);
