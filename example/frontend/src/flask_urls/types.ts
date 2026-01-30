export type StaticReturnType = undefined;
export type StaticArgsType = {filename: string;};

export type MainReturnType = {result: [number | string, boolean | null]; x?: number; y?: boolean;};
export type MainArgsType = undefined;

export type Complex_ReturnType = Record<string, (number | string)[]>;
export type Complex_ArgsType = undefined;

export type WithArgsReturnType = [[boolean, string, boolean], number];
export type WithArgsArgsType = {arg: boolean;};

export type PytestReturnType = Record<string, [boolean[], number[]]>;
export type PytestArgsType = undefined;

