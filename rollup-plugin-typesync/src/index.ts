import { Plugin, PluginContext } from "rollup";
import { SpawnOptionsWithoutStdio, spawn } from "node:child_process";

import fg from "fast-glob";
import path from "node:path";

interface RequiredTypesyncPluginOptions {
    backendRoot: string;
}

interface OptionalTypesyncPluginOptions {
    outDir: string;
    configFile: string;
    translators: string[];
    translatorPriorities: Record<string, number>;
    skipUnannotated: boolean;
    inference: boolean;
    inferenceCanEval: boolean;
    typesFileName: string;
    apisFileName: string;
    returnTypeFormat: string;
    argsTypeFormat: string;
    functionNameFormat: string;
}

export type TypesyncPluginOptions = RequiredTypesyncPluginOptions & Partial<OptionalTypesyncPluginOptions>;

function cmdLineArgsFromOptions(options: Partial<OptionalTypesyncPluginOptions>): string[] {
    const args: string[] = [];
    if (options.outDir) {
        args.push(options.outDir);
    }
    if (options.configFile) {
        args.push("--config");
        args.push(options.configFile);
    }
    for (const translator of options.translators ?? []) {
        args.push("-t");
        args.push(translator);
    }
    for (const [translator, priority] of Object.entries(options.translatorPriorities ?? {})) {
        args.push("--translator-priority");
        args.push(`${translator}:${priority}`);
    }
    if (options.skipUnannotated === false) {
        args.push("--skip-unannotated=false")
    }
    if (options.inference) {
        args.push("-i")
    }
    if (options.inferenceCanEval) {
        args.push("--inference-can-eval")
    }
    if (options.typesFileName) {
        args.push("--types-file");
        args.push(options.typesFileName);
    }
    if (options.apisFileName) {
        args.push("--apis-file");
        args.push(options.apisFileName);
    }
    if (options.returnTypeFormat) {
        args.push("--return-type-format");
        args.push(options.returnTypeFormat);
    }
    if (options.argsTypeFormat) {
        args.push("--args-type-format");
        args.push(options.argsTypeFormat);
    }
    if (options.functionNameFormat) {
        args.push("--function-name-format");
        args.push(options.functionNameFormat);
    }
    return args;
}

async function aspawn(command: string, args: readonly string[] | undefined, options?: SpawnOptionsWithoutStdio | undefined): Promise<{status: number|null, output: string}> {
    const child = spawn(command, args, options);
    let output = "";
    const status = await new Promise<number|null>(resolve => {
        for (const stream of [child.stderr, child.stdout]) {
            stream.on("data", (chunk: string) => output += chunk);
        }
        child.on("close", code => resolve(code));
        child.on("exit", code => resolve(code));
    });
    return { status, output };
}

async function runCodegen(this: PluginContext, options: TypesyncPluginOptions) {
    const {
        backendRoot,
    } = options;

    const result = await aspawn(
        "flask",
        [
            "typesync",
            "generate",
            ...cmdLineArgsFromOptions(options)
        ],
        {
            cwd: path.resolve(backendRoot),
            shell: process.platform === "win32",
        }
    );

    for (const line of result.output.split("\n")) {
        if (line.startsWith("Warning: ")) {
            this.warn(line.substring(9));
        }
    }

    if (result.status !== 0) {
       this.warn(`codegen failed with status ${result.status}`);
    }
    else {
        this.info("codegen finished")
    }
}

export default function TypesyncPlugin(options: TypesyncPluginOptions): Plugin {
    return {
        name: "typesync",
        async buildStart() {
            const files = await fg(path.join(options.backendRoot, "*"), {
                dot: true,
                absolute: true,
                onlyFiles: true,
            });
            for (const file of files) {
                this.addWatchFile(file);
            }
            await runCodegen.call(this, options);
        },
        async watchChange(id) {
            if (!id.startsWith(path.resolve(options.backendRoot))) return;
            await runCodegen.call(this, options);
        }
    };
}
