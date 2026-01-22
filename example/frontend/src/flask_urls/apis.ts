import * as types from "./types";

const BASE_ENDPOINT = "";

function join(urlPart1: string, urlPart2: string) {
    let url = urlPart1;
    if (!url.endsWith("/") && !urlPart2.startsWith("/")) {
        url += "/";
    }
    else if (url.endsWith("/") && urlPart2.startsWith("/")) {
        url = url.substring(0, -1);
    }
    url += urlPart2;
    return url;
}

async function request(endpoint: string) {
    const req = await fetch(join(BASE_ENDPOINT, endpoint));
    if (!req.ok) throw Error(`Request failed with code ${req.status}.`);
    const json = await req.json();
    return json;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function buildUrl(rule: string, params: Record<string, any>) {
    return rule.replace(/<([a-zA-Z_]+[a-zA-Z_0-9]*)>/, (_, key) => {
        return String(params[key]);
    });
}

export function urlFor_static(params: types.static_ArgsType): string {
    const endpoint = buildUrl("/static/<filename>", params);
    return endpoint;
}

export async function request_static(params: types.static_ArgsType): Promise<types.static_ReturnType> {
    const endpoint = urlFor_static(params);
    return await request(endpoint);
}

export function urlFor_main(): string {
    const endpoint = "/main";
    return endpoint;
}

export async function request_main(): Promise<types.main_ReturnType> {
    const endpoint = urlFor_main();
    return await request(endpoint);
}

export function urlFor_complex_(): string {
    const endpoint = "/complex";
    return endpoint;
}

export async function request_complex_(): Promise<types.complex__ReturnType> {
    const endpoint = urlFor_complex_();
    return await request(endpoint);
}

export function urlFor_with_args(params: types.with_args_ArgsType): string {
    const endpoint = buildUrl("/with/<arg>/args", params);
    return endpoint;
}

export async function request_with_args(params: types.with_args_ArgsType): Promise<types.with_args_ReturnType> {
    const endpoint = urlFor_with_args(params);
    return await request(endpoint);
}

export function urlFor_pytest(): string {
    const endpoint = "/pytest";
    return endpoint;
}

export async function request_pytest(): Promise<types.pytest_ReturnType> {
    const endpoint = urlFor_pytest();
    return await request(endpoint);
}
