export class Point2D {
    x: number = null as unknown as number;
    y: number = null as unknown as number;
    visible: boolean = null as unknown as boolean;
    opacity: number = 1;

    constructor(x: number, y: number, visible: boolean, opacity: number = 1) {
        this.x = x;
        this.y = y;
        this.visible = visible;
        this.opacity = opacity;
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