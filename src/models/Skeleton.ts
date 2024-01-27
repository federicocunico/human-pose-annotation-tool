import type { Color, Mesh, Vector3 } from "three";
import { MeshLink } from "@/three_wrapper/MeshLink";

class Skeleton {
    name: string = "";
    joints: Array<Vector3> = [];
    links: Array<Array<number>> = [];

    spheres: Array<Mesh> = [];
    linksMesh: Array<MeshLink> = [];

    colors: Array<Color> = [];
    jointRadius: number = 0.1;

    constructor(
        points: Array<Vector3>,
        colors: Array<Color> = [],
        links: Array<Array<number>> = [],
        name: string = "",
        jointRadius: number = 0.1,
    ) {
        this.name = name;
        this.joints = points;
        this.colors = colors;
        this.links = links;
        this.jointRadius = jointRadius;
    }

    // build(pool: PrimitiveFactory): void {
    //     this.joints.forEach((point, index) => {
    //         let color;
    //         if (this.colors.length < index) {
    //             color = this.colors[index];
    //         }
    //         else {
    //             color = "gray";
    //         }
    //         const sphere = pool.getSphere(this.jointRadius, color);
    //         sphere.position.set(point.x, point.y, point.z);
    //         this.spheres.push(sphere);
    //     });

    //     if (false) {
    //         this.links.forEach((link, index) => {
    //             if (link.length != 2) throw new Error("Link must have two points");
    //             if (link[0] < 0 || link[1] < 0) throw new Error("Link must have positive points");
    //             let pt1 = this.joints[link[0]];
    //             let pt2 = this.joints[link[1]];

    //             const linkMesh = pool.getLink(pt1, pt2);
    //             this.linksMesh.push(linkMesh);
    //         });
    //     }
    // }

    // getMeshToAdd(): Array<Mesh> {
    //     let allMeshes = [] as Array<Mesh>;
    //     allMeshes.push(...this.spheres);
    //     allMeshes.push(...this.linksMesh.map(link => link.mesh));
    //     return allMeshes;
    // }
}

export { Skeleton }
