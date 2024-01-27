import { Mesh, Scene, Vector3, type ColorRepresentation, Line, LineBasicMaterial, BufferGeometry } from "three";
import { createCube, createSphere, createLinkMesh } from "./Geometry";
import { MeshLink } from "./MeshLink";

class Pool<T> {
	pool: T[];

	constructor() {
		this.pool = [];
	}

	get(): T | null {
		if (this.pool.length == 0) {
			return null;
		}
		let candidate: T | null = null;
		for (let i = 0; i < this.pool.length; i++) {

			let mesh = (this.pool[i] as any);
			if (mesh.visible == null && mesh.mesh != null) {
				mesh = mesh.mesh;
			}

			if (mesh.visible == false) {
				candidate = this.pool[i];
				break;
			}

			// // check if typeof is mesh
			// if (this.pool[i] instanceof Mesh || this.pool[i] instanceof Line) {
			//     if (!(this.pool[i] as Mesh).visible) {
			//         candidate = this.pool[i];
			//         break;
			//     }
			// }
			// else {
			//     if ((this.pool[i] as any).mesh.visible == false) {
			//         candidate = this.pool[i];
			//         break;
			//     }
			// }
		}
		return candidate;
	}
	put(obj: T) {
		this.pool.push(obj);
	}

}

class PrimitiveFactory {
	spherePool: Pool<Mesh> = new Pool();
	cubePool: Pool<Mesh> = new Pool();
	linkPool: Pool<MeshLink> = new Pool()
	linePooler: Pool<Line> = new Pool()
	scene: Scene = null as any;

	constructor(scene: Scene) {
		this.scene = scene;
	}


	getSphere(radius: number | null = null, color: ColorRepresentation | null = null): Mesh {
		let candidate = this.spherePool.get();
		if (candidate == null) {
			candidate = createSphere(0.1, "black");
			this.scene.add(candidate);
			this.spherePool.put(candidate);
		}
		if (radius != null) {
			// set radius
			candidate.scale.set(radius, radius, radius);
		}
		if (color != null) {
			// set color
			((candidate.material) as any).color.set(color);
		}
		return candidate;
	}

	getCube(): Mesh {
		let candidate = this.cubePool.get();
		if (candidate == null) {
			candidate = createCube(new Vector3(0.1, 0.1, 0.1), "black");
			this.scene.add(candidate);
			this.cubePool.put(candidate);
		}
		return candidate;
	}

	getLink(pt1: Vector3, pt2: Vector3, color: ColorRepresentation | null = null): MeshLink {
		if (color == null) color = "red";
		let candidate = this.linkPool.get();
		if (candidate == null) {
			candidate = new MeshLink(pt1, pt2)
			this.scene.add(candidate.mesh);
			this.linkPool.put(candidate);
		}
		else {
			candidate.update(pt1, pt2)
		}
		candidate.setColor(color);
		return candidate;
	}

	getLine(pt1: Vector3, pt2: Vector3, color: ColorRepresentation | null = null): Line {
		if (color == null) color = "gray";

		let candidate = this.linePooler.get();
		if (candidate == null) {
			const lineMaterial = new LineBasicMaterial({ color: color });
			const lineGeometry = new BufferGeometry().setFromPoints([pt1, pt2]);
			candidate = new Line(lineGeometry, lineMaterial);
			this.scene.add(candidate);
			this.linePooler.put(candidate);
		}
		else {
			candidate.geometry.setFromPoints([pt1, pt2]);
			(candidate.material as any).color.set(color);
		}
		console.log(candidate)
		candidate.visible = true;
		return candidate;
	}

}

export { PrimitiveFactory }
