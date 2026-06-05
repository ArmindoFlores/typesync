import "./App.css";

import { API } from "./api";
import type { MmGETReturnType } from "./flask_urls/types";
import { useState } from "react";

export default function App() {
    const [endpointReturnValue, setEndpointReturnValue] = useState<MmGETReturnType>();

    const requestEndpoint = async () => {
        const result = await API.getMm({});
        setEndpointReturnValue(result);
    }

    return (
        <div className="main">
            <h1>Typescript Flask URLs</h1>
            <div className="card">
                <button
                    onClick={requestEndpoint}
                >Make Request</button>
            </div>
            <p>
                Endpoint return:
            </p>
                <pre>
                    <code>
                        { JSON.stringify(endpointReturnValue) }
                    </code>
                </pre>
        </div>
    );
}
