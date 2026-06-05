import * as types from "./types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function buildUrl(rule: string, params: Record<string, any>) {
    return rule.replace(/<([a-zA-Z_]+[a-zA-Z_0-9]*)>/, (_, key) => {
        return String(params[key]);
    });
}

export function makeAPI<ExtraArgsType = unknown>(requestFn: types.RequestFunction<ExtraArgsType>) {
    async function getComplex_(params: types.Complex_GETArgsType, extra?: ExtraArgsType): Promise<types.Complex_GETReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "GET", ...params},
            extra,
        );
    }

    async function headComplex_(params: types.Complex_HEADArgsType, extra?: ExtraArgsType): Promise<types.Complex_HEADReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params},
            extra,
        );
    }

    async function optionsComplex_(params: types.Complex_OPTIONSArgsType, extra?: ExtraArgsType): Promise<types.Complex_OPTIONSReturnType> {
        const endpoint = "/complex";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params},
            extra,
        );
    }

    async function getMain(params: types.MainGETArgsType, extra?: ExtraArgsType): Promise<types.MainGETReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "GET", ...params},
            extra,
        );
    }

    async function headMain(params: types.MainHEADArgsType, extra?: ExtraArgsType): Promise<types.MainHEADReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params},
            extra,
        );
    }

    async function optionsMain(params: types.MainOPTIONSArgsType, extra?: ExtraArgsType): Promise<types.MainOPTIONSReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params},
            extra,
        );
    }

    async function postMain(params: types.MainPOSTArgsType, extra?: ExtraArgsType): Promise<types.MainPOSTReturnType> {
        const endpoint = "/main";
        return await requestFn(
            endpoint,
            {method: "POST", ...params},
            extra,
        );
    }

    async function getMm(params: types.MmGETArgsType, extra?: ExtraArgsType): Promise<types.MmGETReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "GET", ...params},
            extra,
        );
    }

    async function headMm(params: types.MmHEADArgsType, extra?: ExtraArgsType): Promise<types.MmHEADReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params},
            extra,
        );
    }

    async function optionsMm(params: types.MmOPTIONSArgsType, extra?: ExtraArgsType): Promise<types.MmOPTIONSReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params},
            extra,
        );
    }

    async function optionsMmPost(params: types.MmPostOPTIONSArgsType, extra?: ExtraArgsType): Promise<types.MmPostOPTIONSReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params},
            extra,
        );
    }

    async function postMmPost(params: types.MmPostPOSTArgsType, extra?: ExtraArgsType): Promise<types.MmPostPOSTReturnType> {
        const endpoint = "/mm";
        return await requestFn(
            endpoint,
            {method: "POST", ...params},
            extra,
        );
    }

    async function optionsPydantic(params: types.PydanticOPTIONSArgsType, extra?: ExtraArgsType): Promise<types.PydanticOPTIONSReturnType> {
        const endpoint = "/pydantic";
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params},
            extra,
        );
    }

    async function postPydantic(params: types.PydanticPOSTArgsType, extra?: ExtraArgsType): Promise<types.PydanticPOSTReturnType> {
        const endpoint = "/pydantic";
        return await requestFn(
            endpoint,
            {method: "POST", ...params},
            extra,
        );
    }

    async function getStatic(params: types.StaticGETArgsType, extra?: ExtraArgsType): Promise<types.StaticGETReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "GET", ...params},
            extra,
        );
    }

    async function headStatic(params: types.StaticHEADArgsType, extra?: ExtraArgsType): Promise<types.StaticHEADReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params},
            extra,
        );
    }

    async function optionsStatic(params: types.StaticOPTIONSArgsType, extra?: ExtraArgsType): Promise<types.StaticOPTIONSReturnType> {
        const endpoint = buildUrl("/static/<filename>", params.args);
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params},
            extra,
        );
    }

    async function getWithArgs(params: types.WithArgsGETArgsType, extra?: ExtraArgsType): Promise<types.WithArgsGETReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "GET", ...params},
            extra,
        );
    }

    async function headWithArgs(params: types.WithArgsHEADArgsType, extra?: ExtraArgsType): Promise<types.WithArgsHEADReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "HEAD", ...params},
            extra,
        );
    }

    async function optionsWithArgs(params: types.WithArgsOPTIONSArgsType, extra?: ExtraArgsType): Promise<types.WithArgsOPTIONSReturnType> {
        const endpoint = buildUrl("/with/<arg>/args", params.args);
        return await requestFn(
            endpoint,
            {method: "OPTIONS", ...params},
            extra,
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
        optionsMmPost,
        postMmPost,
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
