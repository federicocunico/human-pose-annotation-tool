class UriBuilder {
    serverIp: string;
    // serverPort: string | number;
    api: string;
    protocol: string;
    params: string[] = [];

    constructor(serverUrl: string, api: string, protocol: string = "http") {
        this.serverIp = serverUrl;
        this.api = api;
        this.protocol = protocol;
        // this.serverPort = serverPort;
    }

    addParam(key: string, value: string): void {
        this.params.push(`${key}=${value}`);
    }

    build(): string {
        return `${this.protocol}://${this.serverIp}/${this.api}?${this.params.join("&")}`;
    }
}

function defualtUriBuilder(action: string): string {
    let baseUrl = "http://" + window.remoteWebServerUrl;

    // if action does not start with a / then add one
    if (action[0] != "/") {
        action = "/" + action;
    }
    let url = baseUrl + action;
    return url;
}

export { UriBuilder, defualtUriBuilder }
