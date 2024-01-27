export class Point2D {
    x: number = null as unknown as number;
    y: number = null as unknown as number;
    visible: boolean = null as unknown as boolean;

    constructor(x: number, y: number, visible: boolean) {
        this.x = x;
        this.y = y;
        this.visible = visible;
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