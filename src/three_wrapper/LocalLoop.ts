import type { PerspectiveCamera, Scene, WebGLRenderer } from "three";
import type { Loop } from "./Loop";

class LocalLoop implements Loop {
    camera: PerspectiveCamera
    scene: Scene
    renderer: WebGLRenderer

    constructor(camera: PerspectiveCamera, scene: Scene, renderer: WebGLRenderer) {
        this.camera = camera;
        this.scene = scene;
        this.renderer = renderer;
    }

    start() {
        this.renderer.setAnimationLoop(() => {
            this.update();
            // render a frame
            this.renderer.render(this.scene, this.camera);
        });
    }

    stop() {
        this.renderer.setAnimationLoop(null);
    }

    update() {
        // const delta = clock.getDelta();
        // this.renderer.render(this.scene, this.camera);
        // // for (const object of this.updatables) {
        // //     // console.log(object);
        // //     // object.tick(delta);
        // // }

        // Identity function, updated from world.setUpdateFunction()
    }
}

export { LocalLoop }