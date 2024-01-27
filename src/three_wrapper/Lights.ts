import {
    DirectionalLight,
    DirectionalLightHelper,
    Vector3,
    AmbientLight,
    SpotLight,
    type ColorRepresentation,
    Light
} from "three";

function createLights(
    position: Vector3 = new Vector3(0, 100, 100),
    color: ColorRepresentation = "white"
    // ): { light: DirectionalLight, lightHelper: DirectionalLightHelper } {
) {
    // const light = new DirectionalLight(color, 5);
    // const lightHelper = new DirectionalLightHelper(light, 0);
    // light.position.set(position.x, position.y, position.z);
    // light.target.position.set(0, 0, 0);
    // return light;

    const light = new AmbientLight(color, 5);
    return light;
}

export { createLights };
