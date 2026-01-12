export type static_ReturnType = undefined;
export type static_ArgsType = {filename: string;};

export type main_ReturnType = {result: [number | string, boolean | null]; x?: number; y?: boolean;};
export type main_ArgsType = undefined;

export type complex_ReturnType = Record<string, (number | string)[]>;
export type complex_ArgsType = undefined;

export type with_args_ReturnType = [[boolean, string, boolean], number];
export type with_args_ArgsType = {arg: boolean;};

export type pytest_ReturnType = Record<string, [boolean[], number[]]>;
export type pytest_ArgsType = undefined;

