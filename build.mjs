import { mkdir, rm, cp } from "node:fs/promises";
import { resolve } from "node:path";

const root = process.cwd();
const dist = resolve(root, "dist");

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

const filesToCopy = [
  "index.html",
  "Alkhansae_CV 2026.docx",
  "WhatsApp Image 2025-06-07 à 12.37.23_bd4a3f26.jpg",
  ".openai/hosting.json",
];

for (const file of filesToCopy) {
  await cp(resolve(root, file), resolve(dist, file), { recursive: true });
}

