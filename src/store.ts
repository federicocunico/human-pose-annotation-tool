import { defineStore } from 'pinia'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useStore = defineStore('main', {
    state: () => ({
        remoteWebServerUrl: window.remoteWebServerUrl,
        errorMessage: null as string | null,
        currFileIndex: null as number | null,
        temporaryHiddenIndexes: {} as { [key: string]: boolean },
    }),
    getters: {
    }
})