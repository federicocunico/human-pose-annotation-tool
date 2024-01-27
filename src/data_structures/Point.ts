export class Point2D {
    x: number = null as unknown as number;
    y: number = null as unknown as number;

    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }
}

export class Point3D {
    x: number = null as unknown as number;
    y: number = null as unknown as number;
    z: number = null as unknown as number;

    constructor(x: number, y: number, z: number) {
        this.x = x;
        this.y = y;
        this.z = z
    }
}