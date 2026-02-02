import * as types from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function buildUrl(rule: string, params: Record<string, any>) {
    return rule.replace(/<([a-zA-Z_]+[a-zA-Z_0-9]*)>/, (_, key) => {
        return String(params[key]);
    });
}

export function makeAPI(requestFn: types.RequestFunction) {
    async function optionsStatic(params: types.StaticArgsType): Promise<types.StaticReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getStatic(params: types.StaticArgsType): Promise<types.StaticReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headStatic(params: types.StaticArgsType): Promise<types.StaticReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsMain(params: types.MainArgsType): Promise<types.MainReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getMain(params: types.MainArgsType): Promise<types.MainReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headMain(params: types.MainArgsType): Promise<types.MainReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function postMain(params: types.MainArgsType): Promise<types.MainReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "POST", ...params}
        );
    }

    async function optionsComplex_(params: types.Complex_ArgsType): Promise<types.Complex_ReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getComplex_(params: types.Complex_ArgsType): Promise<types.Complex_ReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headComplex_(params: types.Complex_ArgsType): Promise<types.Complex_ReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsWithArgs(params: types.WithArgsArgsType): Promise<types.WithArgsReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getWithArgs(params: types.WithArgsArgsType): Promise<types.WithArgsReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headWithArgs(params: types.WithArgsArgsType): Promise<types.WithArgsReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsPytest(params: types.PytestArgsType): Promise<types.PytestReturnType> {
        const endpoint = "/pytest";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getPytest(params: types.PytestArgsType): Promise<types.PytestReturnType> {
        const endpoint = "/pytest";
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headPytest(params: types.PytestArgsType): Promise<types.PytestReturnType> {
        const endpoint = "/pytest";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsInferred(params: types.InferredArgsType): Promise<types.InferredReturnType> {
        const endpoint = "/inferred";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getInferred(params: types.InferredArgsType): Promise<types.InferredReturnType> {
        const endpoint = "/inferred";
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headInferred(params: types.InferredArgsType): Promise<types.InferredReturnType> {
        const endpoint = "/inferred";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    return {
        optionsStatic,
        getStatic,
        headStatic,
        optionsMain,
        getMain,
        headMain,
        postMain,
        optionsComplex_,
        getComplex_,
        headComplex_,
        optionsWithArgs,
        getWithArgs,
        headWithArgs,
        optionsPytest,
        getPytest,
        headPytest,
        optionsInferred,
        getInferred,
        headInferred,
    };
}
