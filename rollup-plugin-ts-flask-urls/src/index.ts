import { Plugin } from "rollup";
import { spawn, SpawnOptionsWithoutStdio } from "node:child_process";
import path from "node:path";
import fg from "fast-glob";

export interface TsFlaskUrlsPluginOptions {
    outDir: string;
    backendRoot: string;
    cliCommand?: string;
    watchBackend?: boolean;
}

async function aspawn(command: string, args: readonly string[] | undefined, options?: SpawnOptionsWithoutStdio | undefined): Promise<number|null> {
    const child = spawn(command, args, options);
    const status = await new Promise<number|null>(resolve => {
        child.on("close", code => resolve(code));
        child.on("exit", code => resolve(code));
    });
    return status;
}

async function runCodegen(options: TsFlaskUrlsPluginOptions) {
    const {
        backendRoot,
        outDir,
    } = options;

    const status = await aspawn(
        "flask",
        [
            "ts-flask-urls",
            "map-urls",
            path.resolve(outDir),
        ],
        {
            cwd: path.resolve(backendRoot),
            shell: process.platform === "win32"
        }
    );
    if (status !== 0) {
        throw new Error(`ts-flask-urls codegen failed with status ${status}`);
    }
}

export default function tsFlaskUrlsPlugin(options: TsFlaskUrlsPluginOptions): Plugin {
    return {
        name: "ts-flask-urls",
        async buildStart() {
            const files = await fg(path.join(options.backendRoot, "*"), {
                dot: true,
                absolute: true,
                onlyFiles: true,
            });
            for (const file of files) {
                this.addWatchFile(file);
            }
            await runCodegen(options);
        },
        async watchChange(id) {
            if (!id.startsWith(path.resolve(options.backendRoot))) return;
            await runCodegen(options);
        }
    };
}
