import { makeAPI } from "./flask_urls/apis";

const BASE_ENDPOINT = "http://127.0.0.1:5000";

function join(s1: string, s2: string) {
    let path = s1;
    if (s1.endsWith("/") && s2.startsWith("/")) {
        path += s2.substring(1);
    }
    else if (!s1.endsWith("/") && !s2.startsWith("/")) {
        path += "/" + s2;
    }
    else {
        path += s2;
    }
    return path;
}

async function requestFn(endpoint: string) {
    const req = await fetch(join(BASE_ENDPOINT, endpoint));
    return await req.json();
}

export const API = makeAPI(requestFn);
