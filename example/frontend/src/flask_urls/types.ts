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

export type StaticReturnType = undefined;
type _staticArgs = {filename: string;};
type _staticBody = undefined;
export interface StaticArgsType extends RequestArgs {
    args: _staticArgs;
    body?: _staticBody;
}

export type MainReturnType = {result: [number | string, boolean | null]; x?: number; y?: boolean;};
type _mainArgs = undefined;
type _mainBody = undefined;
export interface MainArgsType extends RequestArgs {
    args?: _mainArgs;
    body?: _mainBody;
}

export type Complex_ReturnType = Record<string, (number | string)[]>;
type _complex_Args = undefined;
type _complex_Body = undefined;
export interface Complex_ArgsType extends RequestArgs {
    args?: _complex_Args;
    body?: _complex_Body;
}

export type WithArgsReturnType = [[boolean, string, boolean], number];
type _with_argsArgs = {arg: boolean;};
type _with_argsBody = undefined;
export interface WithArgsArgsType extends RequestArgs {
    args: _with_argsArgs;
    body?: _with_argsBody;
}

export type PytestReturnType = Record<string, [boolean[], number[]]>;
type _pytestArgs = undefined;
type _pytestBody = number;
export interface PytestArgsType extends RequestArgs {
    args?: _pytestArgs;
    body: _pytestBody;
}

export type InferredReturnType = undefined;
type _inferredArgs = undefined;
type _inferredBody = undefined;
export interface InferredArgsType extends RequestArgs {
    args?: _inferredArgs;
    body?: _inferredBody;
}

