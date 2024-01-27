import { Clock, WebGLRenderer, Scene, PerspectiveCamera } from 'three';

const clock = new Clock();

interface Loop {
    camera: PerspectiveCamera;
    scene: Scene;
    renderer: WebGLRenderer;
    start: () => void;
    stop: () => void;
    update: () => void;
}

export type { Loop }

