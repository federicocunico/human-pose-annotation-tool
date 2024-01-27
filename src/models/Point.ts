import { Vector3, type ColorRepresentation } from "three";

class Point {
    location: Vector3 | undefined;
    size: number | undefined;
    color: ColorRepresentation | undefined;

    constructor(location: Vector3, size: number, color: ColorRepresentation) {
        this.location = location;
        this.size = size;
        this.color = color;
    }
}

export { Point }