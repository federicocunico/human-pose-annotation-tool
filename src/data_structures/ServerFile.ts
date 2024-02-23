export default class ServerFile {
    filename: string;
    hasAnnotation: boolean;
    hasSourceData: boolean;

    constructor(filename: string, hasAnnotation: boolean, hasSource: boolean) {
        this.filename = filename;
        this.hasAnnotation = hasAnnotation;
        this.hasSourceData = hasSource;
    }
}