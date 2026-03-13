#!/usr/bin/env node

const DEFAULT_PORT = 9222;
const DEFAULT_HOST = "127.0.0.1";
const DEFAULT_URL = "https://sa-manager.lionabc.com/";
const DEFAULT_COOKIE_NAME = "intlAuthToken";
const DEFAULT_TIMEOUT_MS = 15000;

function printUsage() {
  console.error(
    [
      "Usage: node get_token_via_cdp.js [--port 9222] [--host 127.0.0.1] [--url https://sa-manager.lionabc.com/] [--cookie intlAuthToken] [--timeout 15000]",
      "",
      "Reads a cookie value from a Chrome instance started with --remote-debugging-port.",
    ].join("\n"),
  );
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

function parseInteger(name, value) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    fail(`Invalid ${name}: ${value}`);
  }
  return parsed;
}

function parseArgs(argv) {
  const options = {
    port: DEFAULT_PORT,
    host: DEFAULT_HOST,
    url: DEFAULT_URL,
    cookieName: DEFAULT_COOKIE_NAME,
    timeoutMs: DEFAULT_TIMEOUT_MS,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") {
      printUsage();
      process.exit(0);
    }

    const nextValue = () => {
      i += 1;
      if (i >= argv.length) {
        fail(`Missing value for ${arg}`);
      }
      return argv[i];
    };

    if (arg === "--port") {
      options.port = parseInteger("port", nextValue());
    } else if (arg.startsWith("--port=")) {
      options.port = parseInteger("port", arg.split("=", 2)[1]);
    } else if (arg === "--host") {
      options.host = nextValue();
    } else if (arg.startsWith("--host=")) {
      options.host = arg.split("=", 2)[1];
    } else if (arg === "--url") {
      options.url = nextValue();
    } else if (arg.startsWith("--url=")) {
      options.url = arg.split("=", 2)[1];
    } else if (arg === "--cookie") {
      options.cookieName = nextValue();
    } else if (arg.startsWith("--cookie=")) {
      options.cookieName = arg.split("=", 2)[1];
    } else if (arg === "--timeout") {
      options.timeoutMs = parseInteger("timeout", nextValue());
    } else if (arg.startsWith("--timeout=")) {
      options.timeoutMs = parseInteger("timeout", arg.split("=", 2)[1]);
    } else {
      fail(`Unknown argument: ${arg}`);
    }
  }

  let parsedUrl;
  try {
    parsedUrl = new URL(options.url);
  } catch {
    fail(`Invalid URL: ${options.url}`);
  }

  options.origin = parsedUrl.origin;
  options.hostname = parsedUrl.hostname;
  return options;
}

async function fetchJson(url, init) {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function ensureDebuggerAvailable(options) {
  const versionUrl = `http://${options.host}:${options.port}/json/version`;
  try {
    await fetchJson(versionUrl);
  } catch (error) {
    throw new Error(
      [
        `Cannot connect to Chrome CDP at ${versionUrl}.`,
        "Start Chrome with a remote debugging port first, for example:",
        `open -a "Google Chrome" --args --remote-debugging-port=${options.port}`,
      ].join("\n"),
    );
  }
}

async function listTargets(options) {
  return fetchJson(`http://${options.host}:${options.port}/json/list`);
}

function findTarget(targets, origin) {
  return (
    targets.find(
      (target) =>
        target?.type === "page" &&
        typeof target.url === "string" &&
        target.url.startsWith(origin),
    ) || null
  );
}

async function createTarget(options) {
  const createUrl = `http://${options.host}:${options.port}/json/new?${encodeURIComponent(options.url)}`;
  const attempts = [
    { method: "PUT" },
    { method: "GET" },
  ];

  let lastError = null;
  for (const attempt of attempts) {
    try {
      return await fetchJson(createUrl, attempt);
    } catch (error) {
      lastError = error;
    }
  }

  throw new Error(
    `Failed to open ${options.url} in Chrome via CDP: ${lastError?.message || "unknown error"}`,
  );
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

class CdpClient {
  constructor(wsUrl, timeoutMs) {
    this.wsUrl = wsUrl;
    this.timeoutMs = timeoutMs;
    this.nextId = 1;
    this.pending = new Map();
    this.socket = null;
  }

  async connect() {
    await new Promise((resolve, reject) => {
      const socket = new WebSocket(this.wsUrl);
      this.socket = socket;

      const cleanup = () => {
        socket.removeEventListener("open", onOpen);
        socket.removeEventListener("error", onError);
      };

      const onOpen = () => {
        cleanup();
        resolve();
      };

      const onError = (event) => {
        cleanup();
        reject(event.error || new Error("WebSocket connection failed"));
      };

      socket.addEventListener("open", onOpen);
      socket.addEventListener("error", onError);
      socket.addEventListener("message", (event) => this.handleMessage(event));
      socket.addEventListener("close", () => this.handleClose());
    });
  }

  handleMessage(event) {
    const payload = JSON.parse(event.data.toString());
    if (!payload.id) {
      return;
    }

    const pending = this.pending.get(payload.id);
    if (!pending) {
      return;
    }

    this.pending.delete(payload.id);
    clearTimeout(pending.timer);

    if (payload.error) {
      pending.reject(new Error(payload.error.message || "CDP request failed"));
      return;
    }

    pending.resolve(payload.result || {});
  }

  handleClose() {
    for (const pending of this.pending.values()) {
      clearTimeout(pending.timer);
      pending.reject(new Error("CDP socket closed before the command completed"));
    }
    this.pending.clear();
  }

  async send(method, params = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("CDP socket is not open");
    }

    const id = this.nextId;
    this.nextId += 1;

    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP request timed out: ${method}`));
      }, this.timeoutMs);

      this.pending.set(id, { resolve, reject, timer });
      this.socket.send(payload);
    });
  }

  async close() {
    if (!this.socket) {
      return;
    }

    if (
      this.socket.readyState === WebSocket.CLOSING ||
      this.socket.readyState === WebSocket.CLOSED
    ) {
      return;
    }

    await new Promise((resolve) => {
      this.socket.addEventListener("close", () => resolve(), { once: true });
      this.socket.close();
    });
  }
}

function pickCookie(cookies, options) {
  const matches = cookies.filter((cookie) => {
    if (!cookie || cookie.name !== options.cookieName) {
      return false;
    }

    const domain = String(cookie.domain || "").replace(/^\./, "");
    return domain === options.hostname || options.hostname.endsWith(`.${domain}`);
  });

  if (matches.length === 0) {
    return null;
  }

  return matches.sort((left, right) => Number(Boolean(right.httpOnly)) - Number(Boolean(left.httpOnly)))[0];
}

async function readCookies(client, options) {
  const networkResult = await client.send("Network.getCookies", {
    urls: [options.origin, options.url],
  });
  const fromNetwork = Array.isArray(networkResult.cookies) ? networkResult.cookies : [];

  let fromStorage = [];
  try {
    const storageResult = await client.send("Storage.getCookies");
    fromStorage = Array.isArray(storageResult.cookies) ? storageResult.cookies : [];
  } catch {
    fromStorage = [];
  }

  return [...fromNetwork, ...fromStorage];
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  await ensureDebuggerAvailable(options);

  let target = findTarget(await listTargets(options), options.origin);
  if (!target) {
    target = await createTarget(options);
    await wait(1200);
  }

  if (!target?.webSocketDebuggerUrl) {
    throw new Error(`No debuggable page target found for ${options.origin}`);
  }

  const client = new CdpClient(target.webSocketDebuggerUrl, options.timeoutMs);

  try {
    await client.connect();
    await client.send("Network.enable");
    const cookies = await readCookies(client, options);
    const tokenCookie = pickCookie(cookies, options);

    if (!tokenCookie?.value) {
      throw new Error(
        `Cookie ${options.cookieName} was not found for ${options.hostname}. Please log into the VIPKID admin site in Chrome first.`,
      );
    }

    process.stdout.write(tokenCookie.value);
  } finally {
    await client.close();
  }
}

main().catch((error) => {
  fail(error instanceof Error ? error.message : String(error));
});
