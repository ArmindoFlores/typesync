import * as types from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function buildUrl(rule: string, params: Record<string, any>) {
    return rule.replace(/<([a-zA-Z_]+[a-zA-Z_0-9]*)>/, (_, key) => {
        return String(params[key]);
    });
}

export function makeAPI(requestFn: types.RequestFunction) {
    async function getComplex_(params: types.Complex_GETArgsType): Promise<types.Complex_GETReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headComplex_(params: types.Complex_HEADArgsType): Promise<types.Complex_HEADReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsComplex_(params: types.Complex_OPTIONSArgsType): Promise<types.Complex_OPTIONSReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getMain(params: types.MainGETArgsType): Promise<types.MainGETReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headMain(params: types.MainHEADArgsType): Promise<types.MainHEADReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsMain(params: types.MainOPTIONSArgsType): Promise<types.MainOPTIONSReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function postMain(params: types.MainPOSTArgsType): Promise<types.MainPOSTReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "POST", ...params}
        );
    }

    async function getMm(params: types.MmGETArgsType): Promise<types.MmGETReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headMm(params: types.MmHEADArgsType): Promise<types.MmHEADReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsMm(params: types.MmOPTIONSArgsType): Promise<types.MmOPTIONSReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function optionsPydantic(params: types.PydanticOPTIONSArgsType): Promise<types.PydanticOPTIONSReturnType> {
        const endpoint = "/pydantic";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function postPydantic(params: types.PydanticPOSTArgsType): Promise<types.PydanticPOSTReturnType> {
        const endpoint = "/pydantic";
        return await requestFn(
            endpoint,
            {method: "POST", ...params}
        );
    }

    async function getStatic(params: types.StaticGETArgsType): Promise<types.StaticGETReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headStatic(params: types.StaticHEADArgsType): Promise<types.StaticHEADReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsStatic(params: types.StaticOPTIONSArgsType): Promise<types.StaticOPTIONSReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    async function getWithArgs(params: types.WithArgsGETArgsType): Promise<types.WithArgsGETReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "GET", ...params}
        );
    }

    async function headWithArgs(params: types.WithArgsHEADArgsType): Promise<types.WithArgsHEADReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params}
        );
    }

    async function optionsWithArgs(params: types.WithArgsOPTIONSArgsType): Promise<types.WithArgsOPTIONSReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params}
        );
    }

    return {
        getComplex_,
        headComplex_,
        optionsComplex_,
        getMain,
        headMain,
        optionsMain,
        postMain,
        getMm,
        headMm,
        optionsMm,
        optionsPydantic,
        postPydantic,
        getStatic,
        headStatic,
        optionsStatic,
        getWithArgs,
        headWithArgs,
        optionsWithArgs,
    };
}
