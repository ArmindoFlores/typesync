export interface RequestArgs {
    headers?: Record<string, string>;
}

export interface RequestOptions extends RequestArgs {
    method: string;
    body?: unknown;
}

export type RequestFunction = (
    endpoint: string, options: RequestOptions
// eslint-disable-next-line @typescript-eslint/no-explicit-any
) => Promise<any>;

export type Complex_GETReturnType = Record<string, (number | string)[]>;
type _complex_GETArgs = undefined;
type _complex_GETBody = undefined;
export interface Complex_GETArgsType extends RequestArgs {
    args?: _complex_GETArgs;
    body?: _complex_GETBody;
}

export type Complex_HEADReturnType = Record<string, (number | string)[]>;
type _complex_HEADArgs = undefined;
type _complex_HEADBody = undefined;
export interface Complex_HEADArgsType extends RequestArgs {
    args?: _complex_HEADArgs;
    body?: _complex_HEADBody;
}

export type Complex_OPTIONSReturnType = Record<string, (number | string)[]>;
type _complex_OPTIONSArgs = undefined;
type _complex_OPTIONSBody = undefined;
export interface Complex_OPTIONSArgsType extends RequestArgs {
    args?: _complex_OPTIONSArgs;
    body?: _complex_OPTIONSBody;
}

export type MainGETReturnType = {result: [number | string, boolean | null]; x?: number; y?: boolean;};
type _mainGETArgs = undefined;
type _mainGETBody = undefined;
export interface MainGETArgsType extends RequestArgs {
    args?: _mainGETArgs;
    body?: _mainGETBody;
}

export type MainHEADReturnType = {result: [number | string, boolean | null]; x?: number; y?: boolean;};
type _mainHEADArgs = undefined;
type _mainHEADBody = undefined;
export interface MainHEADArgsType extends RequestArgs {
    args?: _mainHEADArgs;
    body?: _mainHEADBody;
}

export type MainOPTIONSReturnType = {result: [number | string, boolean | null]; x?: number; y?: boolean;};
type _mainOPTIONSArgs = undefined;
type _mainOPTIONSBody = undefined;
export interface MainOPTIONSArgsType extends RequestArgs {
    args?: _mainOPTIONSArgs;
    body?: _mainOPTIONSBody;
}

export type MainPOSTReturnType = {result: [number | string, boolean | null]; x?: number; y?: boolean;};
type _mainPOSTArgs = undefined;
type _mainPOSTBody = undefined;
export interface MainPOSTArgsType extends RequestArgs {
    args?: _mainPOSTArgs;
    body?: _mainPOSTBody;
}

export type MmGETReturnType = {name: string; first_name?: string; age?: number | null; date_birth?: string; is_famous?: boolean;};
type _mmGETArgs = undefined;
type _mmGETBody = undefined;
export interface MmGETArgsType extends RequestArgs {
    args?: _mmGETArgs;
    body?: _mmGETBody;
}

export type MmHEADReturnType = {name: string; first_name?: string; age?: number | null; date_birth?: string; is_famous?: boolean;};
type _mmHEADArgs = undefined;
type _mmHEADBody = undefined;
export interface MmHEADArgsType extends RequestArgs {
    args?: _mmHEADArgs;
    body?: _mmHEADBody;
}

export type MmOPTIONSReturnType = {name: string; first_name?: string; age?: number | null; date_birth?: string; is_famous?: boolean;};
type _mmOPTIONSArgs = undefined;
type _mmOPTIONSBody = undefined;
export interface MmOPTIONSArgsType extends RequestArgs {
    args?: _mmOPTIONSArgs;
    body?: _mmOPTIONSBody;
}

export type PydanticOPTIONSReturnType = Record<string, [boolean[], number[]]>;
type _pydanticOPTIONSArgs = undefined;
type _pydanticOPTIONSBody = any;
export interface PydanticOPTIONSArgsType extends RequestArgs {
    args?: _pydanticOPTIONSArgs;
    body: _pydanticOPTIONSBody;
}

export type PydanticPOSTReturnType = Record<string, [boolean[], number[]]>;
type _pydanticPOSTArgs = undefined;
type _pydanticPOSTBody = any;
export interface PydanticPOSTArgsType extends RequestArgs {
    args?: _pydanticPOSTArgs;
    body: _pydanticPOSTBody;
}

export type StaticGETReturnType = undefined;
type _staticGETArgs = {filename: string;};
type _staticGETBody = undefined;
export interface StaticGETArgsType extends RequestArgs {
    args: _staticGETArgs;
    body?: _staticGETBody;
}

export type StaticHEADReturnType = undefined;
type _staticHEADArgs = {filename: string;};
type _staticHEADBody = undefined;
export interface StaticHEADArgsType extends RequestArgs {
    args: _staticHEADArgs;
    body?: _staticHEADBody;
}

export type StaticOPTIONSReturnType = undefined;
type _staticOPTIONSArgs = {filename: string;};
type _staticOPTIONSBody = undefined;
export interface StaticOPTIONSArgsType extends RequestArgs {
    args: _staticOPTIONSArgs;
    body?: _staticOPTIONSBody;
}

export type WithArgsGETReturnType = [[boolean, string, boolean], number];
type _with_argsGETArgs = {arg: boolean;};
type _with_argsGETBody = undefined;
export interface WithArgsGETArgsType extends RequestArgs {
    args: _with_argsGETArgs;
    body?: _with_argsGETBody;
}

export type WithArgsHEADReturnType = [[boolean, string, boolean], number];
type _with_argsHEADArgs = {arg: boolean;};
type _with_argsHEADBody = undefined;
export interface WithArgsHEADArgsType extends RequestArgs {
    args: _with_argsHEADArgs;
    body?: _with_argsHEADBody;
}

export type WithArgsOPTIONSReturnType = [[boolean, string, boolean], number];
type _with_argsOPTIONSArgs = {arg: boolean;};
type _with_argsOPTIONSBody = undefined;
export interface WithArgsOPTIONSArgsType extends RequestArgs {
    args: _with_argsOPTIONSArgs;
    body?: _with_argsOPTIONSBody;
}
