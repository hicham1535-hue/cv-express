import { mkdir, rm, cp, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = process.cwd();
const dist = resolve(root, "dist");

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });
await mkdir(resolve(dist, "server"), { recursive: true });

const filesToCopy = [
  "index.html",
  "Alkhansae_CV 2026.pdf",
  "WhatsApp Image 2025-06-07 à 12.37.23_bd4a3f26.jpg",
  ".openai/hosting.json",
];

for (const file of filesToCopy) {
  await cp(resolve(root, file), resolve(dist, file), { recursive: true });
}

const assetFiles = [
  {
    path: "/index.html",
    file: resolve(root, "index.html"),
    contentType: "text/html; charset=utf-8",
  },
  {
    path: "/Alkhansae_CV 2026.pdf",
    file: resolve(root, "Alkhansae_CV 2026.pdf"),
    contentType: "application/pdf",
  },
  {
    path: "/WhatsApp Image 2025-06-07 à 12.37.23_bd4a3f26.jpg",
    file: resolve(root, "WhatsApp Image 2025-06-07 à 12.37.23_bd4a3f26.jpg"),
    contentType: "image/jpeg",
  },
];

const assets = [];
for (const asset of assetFiles) {
  const base64 = (await readFile(asset.file)).toString("base64");
  assets.push({
    path: asset.path,
    contentType: asset.contentType,
    base64,
  });
}

const serverBundle = `const ASSETS = new Map(${JSON.stringify(assets)}.map((asset) => [
  asset.path,
  asset,
]));

const CANONICAL_PATH = "/cv-dr-alkhansae";

function toBytes(base64) {
  const bin = atob(base64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function assetResponse(asset) {
  return new Response(toBytes(asset.base64), {
    headers: {
      "content-type": asset.contentType,
      "cache-control": "public, max-age=3600",
    },
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const pathname = decodeURIComponent(url.pathname);

    if (pathname === "/") {
      return Response.redirect(new URL(CANONICAL_PATH, url), 302);
    }

    if (pathname === CANONICAL_PATH) {
      return assetResponse(ASSETS.get("/index.html"));
    }

    if (ASSETS.has(pathname)) {
      return assetResponse(ASSETS.get(pathname));
    }

    return assetResponse(ASSETS.get("/index.html"));
  },
};
`;

await writeFile(resolve(dist, "server", "index.js"), serverBundle);
