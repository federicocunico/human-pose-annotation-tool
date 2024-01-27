class CircularBuffer<T> {
    private buffer: T[] = [];
    private size: number;

    constructor(size: number) {
        this.size = size;
    }

    push(element: T): void {
        if (this.buffer.length >= this.size) {
            this.buffer.shift(); // Remove the oldest element
        }
        this.buffer.push(element);
    }

    getBuffer(): T[] {
        return this.buffer;
    }
}

export { CircularBuffer }