#!/usr/bin/env node

const crypto = require("node:crypto");
const http = require("node:http");
const https = require("node:https");

const DEFAULT_PORT = 9222;
const DEFAULT_HOST = "127.0.0.1";
const DEFAULT_URL = "https://power.lionabc.com/";
const DEFAULT_COOKIE_NAME = "intlAuthToken";
const DEFAULT_TIMEOUT_MS = 15000;
const WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";

function printUsage() {
  console.error(
    [
      "用法：node get_token_via_cdp.js [--port 9222] [--host 127.0.0.1] [--url https://power.lionabc.com/] [--cookie intlAuthToken] [--timeout 15000]",
      "",
      "从已使用 --remote-debugging-port 启动的 Chrome 中读取指定 Cookie。",
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
    fail(`${name} 非法：${value}`);
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
        fail(`参数 ${arg} 缺少值`);
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
      fail(`未知参数：${arg}`);
    }
  }

  let parsedUrl;
  try {
    parsedUrl = new URL(options.url);
  } catch {
    fail(`URL 非法：${options.url}`);
  }

  options.origin = parsedUrl.origin;
  options.hostname = parsedUrl.hostname;
  return options;
}

function requestJson(urlString, init = {}) {
  const urlObject = new URL(urlString);
  const client = urlObject.protocol === "https:" ? https : http;

  return new Promise((resolve, reject) => {
    const request = client.request(
      {
        method: init.method || "GET",
        hostname: urlObject.hostname,
        port: urlObject.port || (urlObject.protocol === "https:" ? 443 : 80),
        path: `${urlObject.pathname}${urlObject.search}`,
        headers: init.headers || {},
      },
      (response) => {
        const chunks = [];
        response.on("data", (chunk) => chunks.push(chunk));
        response.on("end", () => {
          const rawBody = Buffer.concat(chunks).toString("utf8");
          if (response.statusCode < 200 || response.statusCode >= 300) {
            reject(new Error(`${response.statusCode} ${response.statusMessage || ""}`.trim()));
            return;
          }
          try {
            resolve(JSON.parse(rawBody));
          } catch (error) {
            reject(new Error(`返回内容不是合法 JSON：${error.message}`));
          }
        });
      },
    );

    request.on("error", reject);
    request.end(init.body);
  });
}

async function ensureDebuggerAvailable(options) {
  const versionUrl = `http://${options.host}:${options.port}/json/version`;
  try {
    await requestJson(versionUrl);
  } catch (error) {
    throw new Error(
      [
        `无法连接到 Chrome CDP：${versionUrl}`,
        "请先使用远程调试端口启动 Chrome，例如：",
        `open -a "Google Chrome" --args --remote-debugging-port=${options.port}`,
      ].join("\n"),
    );
  }
}

async function listTargets(options) {
  return requestJson(`http://${options.host}:${options.port}/json/list`);
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
      return await requestJson(createUrl, attempt);
    } catch (error) {
      lastError = error;
    }
  }

  throw new Error(
    `无法通过 CDP 在 Chrome 中打开 ${options.url}：${lastError?.message || "未知错误"}`,
  );
}

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function encodeFrame(opcode, payloadBuffer) {
  const payload = Buffer.isBuffer(payloadBuffer) ? payloadBuffer : Buffer.from(payloadBuffer);
  const mask = crypto.randomBytes(4);
  let header;

  if (payload.length < 126) {
    header = Buffer.alloc(2);
    header[1] = 0x80 | payload.length;
  } else if (payload.length <= 0xffff) {
    header = Buffer.alloc(4);
    header[1] = 0x80 | 126;
    header.writeUInt16BE(payload.length, 2);
  } else {
    header = Buffer.alloc(10);
    header[1] = 0x80 | 127;
    header.writeBigUInt64BE(BigInt(payload.length), 2);
  }

  header[0] = 0x80 | opcode;
  const maskedPayload = Buffer.from(payload);
  for (let index = 0; index < maskedPayload.length; index += 1) {
    maskedPayload[index] ^= mask[index % 4];
  }

  return Buffer.concat([header, mask, maskedPayload]);
}

class CdpClient {
  constructor(wsUrl, timeoutMs) {
    this.wsUrl = wsUrl;
    this.timeoutMs = timeoutMs;
    this.nextId = 1;
    this.pending = new Map();
    this.socket = null;
    this.buffer = Buffer.alloc(0);
    this.fragmentedOpcode = null;
    this.fragmentedChunks = [];
  }

  async connect() {
    const wsUrl = new URL(this.wsUrl);
    const client = wsUrl.protocol === "wss:" ? https : http;
    const key = crypto.randomBytes(16).toString("base64");

    await new Promise((resolve, reject) => {
      const request = client.request({
        protocol: wsUrl.protocol === "wss:" ? "https:" : "http:",
        hostname: wsUrl.hostname,
        port: wsUrl.port || (wsUrl.protocol === "wss:" ? 443 : 80),
        path: `${wsUrl.pathname}${wsUrl.search}`,
        headers: {
          Connection: "Upgrade",
          Upgrade: "websocket",
          "Sec-WebSocket-Version": "13",
          "Sec-WebSocket-Key": key,
          Host: wsUrl.host,
        },
      });

      request.once("upgrade", (response, socket, head) => {
        const expectedAccept = crypto
          .createHash("sha1")
          .update(`${key}${WS_GUID}`)
          .digest("base64");
        if (response.headers["sec-websocket-accept"] !== expectedAccept) {
          reject(new Error("Chrome CDP WebSocket 握手失败。"));
          socket.destroy();
          return;
        }

        this.socket = socket;
        socket.on("data", (chunk) => {
          try {
            this.handleData(chunk);
          } catch (error) {
            this.handleClose(error);
          }
        });
        socket.on("error", (error) => this.handleClose(error));
        socket.on("close", () => this.handleClose());
        if (head?.length) {
          try {
            this.handleData(head);
          } catch (error) {
            this.handleClose(error);
            return;
          }
        }
        resolve();
      });

      request.once("response", (response) => {
        response.resume();
        reject(new Error(`Chrome CDP WebSocket 握手失败：HTTP ${response.statusCode}`));
      });
      request.once("error", reject);
      request.end();
    });
  }

  resetFragmentedMessage() {
    this.fragmentedOpcode = null;
    this.fragmentedChunks = [];
  }

  handleMessageFrame(opcode, payload, isFinalFrame) {
    if (opcode === 0x1) {
      if (isFinalFrame) {
        this.handleMessage(payload.toString("utf8"));
        return;
      }
      this.fragmentedOpcode = opcode;
      this.fragmentedChunks = [Buffer.from(payload)];
      return;
    }

    if (opcode === 0x0) {
      if (this.fragmentedOpcode === null) {
        throw new Error("收到未开始的 CDP 分片消息。");
      }
      this.fragmentedChunks.push(Buffer.from(payload));
      if (!isFinalFrame) {
        return;
      }

      const fullPayload = Buffer.concat(this.fragmentedChunks);
      const originalOpcode = this.fragmentedOpcode;
      this.resetFragmentedMessage();

      if (originalOpcode === 0x1) {
        this.handleMessage(fullPayload.toString("utf8"));
        return;
      }
      throw new Error(`收到不支持的 CDP 分片消息类型：${originalOpcode}`);
    }

    if (opcode === 0x2) {
      throw new Error("收到二进制 CDP 消息，当前脚本无法处理。");
    }
  }

  handleData(chunk) {
    this.buffer = Buffer.concat([this.buffer, chunk]);

    while (this.buffer.length >= 2) {
      const firstByte = this.buffer[0];
      const secondByte = this.buffer[1];
      const isFinalFrame = Boolean(firstByte & 0x80);
      const opcode = firstByte & 0x0f;
      const isMasked = Boolean(secondByte & 0x80);

      let offset = 2;
      let payloadLength = secondByte & 0x7f;

      if (payloadLength === 126) {
        if (this.buffer.length < offset + 2) {
          return;
        }
        payloadLength = this.buffer.readUInt16BE(offset);
        offset += 2;
      } else if (payloadLength === 127) {
        if (this.buffer.length < offset + 8) {
          return;
        }
        const payloadLengthBigInt = this.buffer.readBigUInt64BE(offset);
        if (payloadLengthBigInt > BigInt(Number.MAX_SAFE_INTEGER)) {
          throw new Error("收到过大的 CDP 消息，当前脚本无法处理。");
        }
        payloadLength = Number(payloadLengthBigInt);
        offset += 8;
      }

      let mask;
      if (isMasked) {
        if (this.buffer.length < offset + 4) {
          return;
        }
        mask = this.buffer.slice(offset, offset + 4);
        offset += 4;
      }

      if (this.buffer.length < offset + payloadLength) {
        return;
      }

      let payload = this.buffer.slice(offset, offset + payloadLength);
      this.buffer = this.buffer.slice(offset + payloadLength);

      if (isMasked) {
        payload = Buffer.from(payload);
        for (let index = 0; index < payload.length; index += 1) {
          payload[index] ^= mask[index % 4];
        }
      }

      if (opcode === 0x1 || opcode === 0x0 || opcode === 0x2) {
        this.handleMessageFrame(opcode, payload, isFinalFrame);
      } else if (opcode === 0x8) {
        this.handleClose();
        return;
      } else if (opcode === 0x9) {
        this.writeFrame(0x0a, payload);
      }
    }
  }

  handleMessage(rawMessage) {
    const payload = JSON.parse(rawMessage);
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
      pending.reject(new Error(payload.error.message || "CDP 请求失败"));
      return;
    }

    pending.resolve(payload.result || {});
  }

  handleClose(error) {
    this.resetFragmentedMessage();
    for (const pending of this.pending.values()) {
      clearTimeout(pending.timer);
      pending.reject(error || new Error("CDP 连接在命令完成前已关闭"));
    }
    this.pending.clear();
  }

  writeFrame(opcode, payload) {
    if (!this.socket || this.socket.destroyed) {
      throw new Error("CDP 连接尚未建立");
    }
    this.socket.write(encodeFrame(opcode, payload));
  }

  async send(method, params = {}) {
    if (!this.socket || this.socket.destroyed) {
      throw new Error("CDP 连接尚未建立");
    }

    const id = this.nextId;
    this.nextId += 1;

    const payload = JSON.stringify({ id, method, params });
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP 请求超时：${method}`));
      }, this.timeoutMs);

      this.pending.set(id, { resolve, reject, timer });
      this.writeFrame(0x1, payload);
    });
  }

  async close() {
    if (!this.socket || this.socket.destroyed) {
      return;
    }

    await new Promise((resolve) => {
      this.socket.once("close", resolve);
      this.socket.end(encodeFrame(0x8, Buffer.alloc(0)));
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
    throw new Error(`没有找到可调试的页面：${options.origin}`);
  }

  const client = new CdpClient(target.webSocketDebuggerUrl, options.timeoutMs);

  try {
    await client.connect();
    await client.send("Network.enable");
    const cookies = await readCookies(client, options);
    const tokenCookie = pickCookie(cookies, options);

    if (!tokenCookie?.value) {
      throw new Error(
        `未在 ${options.hostname} 下找到 Cookie ${options.cookieName}，请先在 Chrome 中完成登录。`,
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
