export interface RequestArgs {
    headers?: Record<string, string>;
}

export interface RequestOptions extends RequestArgs {
    method: string;
    body?: unknown;
}

export type RequestFunction<ExtraArgsType> = (
    endpoint: string,
    options: RequestOptions,
    extra?: ExtraArgsType,
// eslint-disable-next-line @typescript-eslint/no-explicit-any
) => Promise<any>;

export type Complex_GETReturnType = Record<string, (number | string)[]>;
type _complex_GETArgs = never;
type _complex_GETBody = never;
export interface Complex_GETArgsType extends RequestArgs {
    args?: _complex_GETArgs;
    body?: _complex_GETBody;
}

export type Complex_HEADReturnType = Record<string, (number | string)[]>;
type _complex_HEADArgs = never;
type _complex_HEADBody = never;
export interface Complex_HEADArgsType extends RequestArgs {
    args?: _complex_HEADArgs;
    body?: _complex_HEADBody;
}

export type Complex_OPTIONSReturnType = Record<string, (number | string)[]>;
type _complex_OPTIONSArgs = never;
type _complex_OPTIONSBody = never;
export interface Complex_OPTIONSArgsType extends RequestArgs {
    args?: _complex_OPTIONSArgs;
    body?: _complex_OPTIONSBody;
}

export type MainGETReturnType = {result: [boolean | null, number | string]; x?: number; y?: boolean;};
type _mainGETArgs = never;
type _mainGETBody = never;
export interface MainGETArgsType extends RequestArgs {
    args?: _mainGETArgs;
    body?: _mainGETBody;
}

export type MainHEADReturnType = {result: [boolean | null, number | string]; x?: number; y?: boolean;};
type _mainHEADArgs = never;
type _mainHEADBody = never;
export interface MainHEADArgsType extends RequestArgs {
    args?: _mainHEADArgs;
    body?: _mainHEADBody;
}

export type MainOPTIONSReturnType = {result: [boolean | null, number | string]; x?: number; y?: boolean;};
type _mainOPTIONSArgs = never;
type _mainOPTIONSBody = never;
export interface MainOPTIONSArgsType extends RequestArgs {
    args?: _mainOPTIONSArgs;
    body?: _mainOPTIONSBody;
}

export type MainPOSTReturnType = {result: [boolean | null, number | string]; x?: number; y?: boolean;};
type _mainPOSTArgs = never;
type _mainPOSTBody = never;
export interface MainPOSTArgsType extends RequestArgs {
    args?: _mainPOSTArgs;
    body?: _mainPOSTBody;
}

export type MmGETReturnType = {name: string; first_name?: string; age?: null | number; date_birth: string; is_famous?: boolean;};
type _mmGETArgs = never;
type _mmGETBody = never;
export interface MmGETArgsType extends RequestArgs {
    args?: _mmGETArgs;
    body?: _mmGETBody;
}

export type MmHEADReturnType = {name: string; first_name?: string; age?: null | number; date_birth: string; is_famous?: boolean;};
type _mmHEADArgs = never;
type _mmHEADBody = never;
export interface MmHEADArgsType extends RequestArgs {
    args?: _mmHEADArgs;
    body?: _mmHEADBody;
}

export type MmOPTIONSReturnType = {name: string; first_name?: string; age?: null | number; date_birth: string; is_famous?: boolean;};
type _mmOPTIONSArgs = never;
type _mmOPTIONSBody = never;
export interface MmOPTIONSArgsType extends RequestArgs {
    args?: _mmOPTIONSArgs;
    body?: _mmOPTIONSBody;
}

export type MmPostOPTIONSReturnType = object;
type _mm_postOPTIONSArgs = never;
type _mm_postOPTIONSBody = {name: string; date_birth: string; is_famous?: boolean;};
export interface MmPostOPTIONSArgsType extends RequestArgs {
    args?: _mm_postOPTIONSArgs;
    body: _mm_postOPTIONSBody;
}

export type MmPostPOSTReturnType = object;
type _mm_postPOSTArgs = never;
type _mm_postPOSTBody = {name: string; date_birth: string; is_famous?: boolean;};
export interface MmPostPOSTArgsType extends RequestArgs {
    args?: _mm_postPOSTArgs;
    body: _mm_postPOSTBody;
}

export type PydanticOPTIONSReturnType = Record<string, [boolean[], number[]]>;
type _pydanticOPTIONSArgs = never;
type _pydanticOPTIONSBody = {x: number;};
export interface PydanticOPTIONSArgsType extends RequestArgs {
    args?: _pydanticOPTIONSArgs;
    body: _pydanticOPTIONSBody;
}

export type PydanticPOSTReturnType = Record<string, [boolean[], number[]]>;
type _pydanticPOSTArgs = never;
type _pydanticPOSTBody = {x: number;};
export interface PydanticPOSTArgsType extends RequestArgs {
    args?: _pydanticPOSTArgs;
    body: _pydanticPOSTBody;
}

export type StaticGETReturnType = undefined;
type _staticGETArgs = {filename: string;};
type _staticGETBody = never;
export interface StaticGETArgsType extends RequestArgs {
    args: _staticGETArgs;
    body?: _staticGETBody;
}

export type StaticHEADReturnType = undefined;
type _staticHEADArgs = {filename: string;};
type _staticHEADBody = never;
export interface StaticHEADArgsType extends RequestArgs {
    args: _staticHEADArgs;
    body?: _staticHEADBody;
}

export type StaticOPTIONSReturnType = undefined;
type _staticOPTIONSArgs = {filename: string;};
type _staticOPTIONSBody = never;
export interface StaticOPTIONSArgsType extends RequestArgs {
    args: _staticOPTIONSArgs;
    body?: _staticOPTIONSBody;
}

export type WithArgsGETReturnType = [[boolean, boolean, string], number];
type _with_argsGETArgs = {arg: boolean;};
type _with_argsGETBody = never;
export interface WithArgsGETArgsType extends RequestArgs {
    args: _with_argsGETArgs;
    body?: _with_argsGETBody;
}

export type WithArgsHEADReturnType = [[boolean, boolean, string], number];
type _with_argsHEADArgs = {arg: boolean;};
type _with_argsHEADBody = never;
export interface WithArgsHEADArgsType extends RequestArgs {
    args: _with_argsHEADArgs;
    body?: _with_argsHEADBody;
}

export type WithArgsOPTIONSReturnType = [[boolean, boolean, string], number];
type _with_argsOPTIONSArgs = {arg: boolean;};
type _with_argsOPTIONSBody = never;
export interface WithArgsOPTIONSArgsType extends RequestArgs {
    args: _with_argsOPTIONSArgs;
    body?: _with_argsOPTIONSBody;
}

