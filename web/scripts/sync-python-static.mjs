import { cp, mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";
const source = resolve("dist/client");
const target = resolve("../shamaran/web/static");
await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });
await cp(source, target, { recursive: true });
console.log(`Synced Web UI to ${target}`);
