import { BasicShadowMap, PCFSoftShadowMap, WebGLRenderer } from "three";

function createRenderer(canvas: any) {
    const renderer = new WebGLRenderer({ antialias: true, canvas: canvas });

    // Enable shadows in the renderer
    // renderer.shadowMap.enabled = true;
    // renderer.shadowMap.type = PCFSoftShadowMap;
    // renderer.shadowMap.type = BasicShadowMap;
    // renderer.shadowMap.autoUpdate = true;
    // renderer.shadowMap.needsUpdate = true;

    // Turn on the physically correct lighting model.
    // renderer.physicallyCorrectLights = true;
    return renderer;
}

export { createRenderer };
