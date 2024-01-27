declare const SERVER_PORT_FROM_SERVER: number | undefined  // exists in index.html as a global variable

const SERVER_IP = "127.0.0.1"
const SERVER_PORT = SERVER_PORT_FROM_SERVER || 40000
const DATA_API = "data"

export { SERVER_IP, SERVER_PORT, DATA_API }