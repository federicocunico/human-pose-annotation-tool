import { PerspectiveCamera, Vector3 } from 'three';

function createCamera(position: Vector3 = new Vector3(0, 0, -5), fov: number = 35, aspect: number = 1, near: number = 0.1, far: number = 100) {
    const camera = new PerspectiveCamera(
        fov, // FOV = Field Of View
        aspect, // Aspect ratio (dummy value)
        near, // Near clipping plane
        far, // Far clipping plane
    );

    // Move the camera back so we can view the scene
    //      x y  z
    camera.position.set(position.x, position.y, position.z);
    // camera.tick = (delta) => {
    // };

    return camera;
}

export { createCamera };