import * as types from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function buildUrl(rule: string, params: Record<string, any>) {
    return rule.replace(/<([a-zA-Z_]+[a-zA-Z_0-9]*)>/, (_, key) => {
        return String(params[key]);
    });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type RequestFunction = (endpoint: string) => Promise<any>;

export function makeAPI(requestFn: RequestFunction) {
    function urlFor_static(params: types.StaticArgsType): string {
        const endpoint = buildUrl("/static/<filename>", params);
         return endpoint;
    }

    async function requestStatic(params: types.StaticArgsType): Promise<types.StaticReturnType> {
        const endpoint = urlFor_static(params);
        return await requestFn(endpoint);
    }

    function urlFor_main(): string {
        const endpoint = "/main";
         return endpoint;
    }

    async function requestMain(): Promise<types.MainReturnType> {
        const endpoint = urlFor_main();
        return await requestFn(endpoint);
    }

    function urlFor_complex_(): string {
        const endpoint = "/complex";
         return endpoint;
    }

    async function requestComplex_(): Promise<types.Complex_ReturnType> {
        const endpoint = urlFor_complex_();
        return await requestFn(endpoint);
    }

    function urlFor_with_args(params: types.WithArgsArgsType): string {
        const endpoint = buildUrl("/with/<arg>/args", params);
         return endpoint;
    }

    async function requestWithArgs(params: types.WithArgsArgsType): Promise<types.WithArgsReturnType> {
        const endpoint = urlFor_with_args(params);
        return await requestFn(endpoint);
    }

    function urlFor_pytest(): string {
        const endpoint = "/pytest";
         return endpoint;
    }

    async function requestPytest(): Promise<types.PytestReturnType> {
        const endpoint = urlFor_pytest();
        return await requestFn(endpoint);
    }

    return {
        requestStatic,
        requestMain,
        requestComplex_,
        requestWithArgs,
        requestPytest,
    };
}
