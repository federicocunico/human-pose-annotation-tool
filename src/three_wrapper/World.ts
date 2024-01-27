import { createCamera } from "./Camera";
import { createLights } from "./Lights";
import { createScene } from "./Scene";
import { createRenderer } from "./Renderer";
import createTerrain from "./Terrain";
import type { Loop } from "./Loop";
import { Resizer } from "./Resizer";
import { LocalLoop } from "./LocalLoop";
import { PerspectiveCamera, Scene, WebGLRenderer, Vector3, Mesh, MeshStandardMaterial, AxesHelper, type ColorRepresentation, Light, PlaneGeometry, Color } from "three";
import { OrbitControls } from "three/examples/jsm/Addons.js";
import { PrimitiveFactory } from "./Pool";

class World {
    name: string = "";
    camera: PerspectiveCamera = null as any;
    renderer: WebGLRenderer = null as any;
    scene: Scene = null as any;
    loop: Loop = null as any;
    controls: OrbitControls = null as any;

    pooler: PrimitiveFactory = null as any;

    constructor(container: HTMLElement, backgroundColor: string | number = "lightgray", addLights: boolean = true) {
        // Instances of camera, scene, and renderer
        this.camera = createCamera();
        this.scene = createScene(backgroundColor);
        this.renderer = createRenderer(container);

        this.pooler = new PrimitiveFactory(this.scene);

        this.loop = new LocalLoop(this.camera, this.scene, this.renderer);
        // container.appendChild(this.renderer.domElement);

        if (addLights) {
            const light = createLights();
            this.scene.add(light);
        }

        this.loop.start();

        const resizer = new Resizer(container, this.camera, this.renderer);
        resizer.onResize = () => {
            this.render();
        };
    }

    enableControls(enable: boolean): void {
        if (enable) {
            // Add controls for easier navigation
            this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        }
        else {
            this.controls = null as any;
        }
    }

    setUp(addReferenceSystem: boolean = true): void {
        if (addReferenceSystem) {
            this.addReferenceSystem();
        }
        this.addPlane(20, 20, "gray");
    }

    clearWorld(onlyObjects: boolean = true): void {
        this.scene.children.forEach(child => {
            if (onlyObjects) {
                // if a reference system, don't remove it
                if (child instanceof AxesHelper || child instanceof Light) {
                    return;
                }

                if (child instanceof Mesh) {
                    if (child.geometry instanceof PlaneGeometry) {
                        return;
                    }
                    child.visible = false;
                }
            }
            else {
                // this.scene.remove(child);
                child.visible = false;
            }
        });
        // if (onlyObjects) {
        //     // remove all objects from the scene
        //     this.scene.children.forEach(child => {
        //         if (child instanceof Mesh) {
        //             this.scene.remove(child);
        //         }
        //     });
        // }
        // else {
        //     // remove all objects and lights from the scene
        //     this.scene.children.forEach(child => {
        //         this.scene.remove(child);
        //     });
        // }
    }

    setUpdateFunction(updateFunction: any): void {
        this.loop.update = updateFunction;
    }

    setCameraPosition(x: number, y: number, z: number): void {
        this.camera.position.set(x, y, z);
    }

    lookAt(object: any = null): void {
        if (object) {
            this.camera.lookAt(object.position);
        }
        else {
            this.camera.lookAt(new Vector3(0, 0, 0));
        }
    }

    addReferenceSystem(position: Vector3 = new Vector3(0, 0, 0), size: number = 2): void {
        // create a reference system with three axis (x, y, z)
        const axesHelper = new AxesHelper(size); // You can adjust the size of the axes
        axesHelper.position.set(position.x, position.y, position.z);
        // Add the AxesHelper to the scene
        this.scene.add(axesHelper);
    }

    addSkeleton(
        points: Array<Vector3>,
        colors: Array<Color> = [],
        links: Array<Array<number>> = [],
        name: string = "",
    ) {
        let skeletonSize = 0.2;
        points.forEach((point, idx) => {
            let sphere = this.pooler.getSphere(skeletonSize, colors[idx]);
            sphere.visible = true;
            sphere.position.set(point.x, point.y, point.z);
        })

        links.forEach((link, idx) => {
            let pt1 = points[link[0]];
            let pt2 = points[link[1]];
            
            let c1 = colors[link[0]];
            let c2 = colors[link[1]];
            let linkColor;
            if (c1.r == c2.r && c1.g == c2.g && c1.b == c2.b){
                linkColor = c1;
            }
            else{
                linkColor = "gray";
            }

            let linkMesh = this.pooler.getLink(pt1, pt2, linkColor);
            linkMesh.mesh.visible = true;

            // Create line
            // let line = this.pooler.getLine(pt1, pt2, "gray");
            // line.visible = true;
        });
    }

    addPlane(sizeX: number = 20, sizeY: number = 20, color: ColorRepresentation = "gray"): void {
        let terrain = createTerrain(sizeX, sizeY, color);
        this.scene.add(terrain);
        // this.addToWorld(terrain);
    }

    addCube(position: Vector3, size: Vector3, color: ColorRepresentation): Mesh {
        let cube = this.pooler.getCube();
        cube.visible = true;
        cube.scale.set(size.x, size.y, size.z);
        cube.material = new MeshStandardMaterial({ color: color });
        cube.position.set(position.x, position.y, position.z);
        // this.addToWorld(cube);
        return cube;
    }

    addSphere(positionL: Vector3, radius: number, color: ColorRepresentation): Mesh {
        let sphere = this.pooler.getSphere();
        sphere.visible = true;
        sphere.scale.set(radius, radius, radius);
        sphere.material = new MeshStandardMaterial({ color: color });
        sphere.position.set(positionL.x, positionL.y, positionL.z);
        // this.addToWorld(sphere);
        return sphere;
    }

    // addToWorld(object: any): void {
    //     // if object already in scene, set visible=true
    //     // if (this.scene.children.includes(object)) {
    //     //     object.visible = true;
    //     // }
    //     // else {
    //     //     this.scene.add(object);
    //     // }
    // }

    render(): void {
        if (this.controls) {
            this.controls.update();
        }
        // Draw a single frame
        this.renderer.render(this.scene, this.camera);
    }
}
export { World };