import { CylinderGeometry, Mesh, MeshStandardMaterial, Vector3, MathUtils, type ColorRepresentation } from "three";
import { distanceTo } from "./Geometry";

class MeshLink {
	point1 = new Vector3(0, 0, 0);
	point2 = new Vector3(0, 0, 0);
	mesh: Mesh;

	constructor(point1: Vector3, point2: Vector3) {
		this.point1 = point1;
		this.point2 = point2;
		this.mesh = this.build();
	}

	build(): Mesh {
		// create cylinder between two points
		const size = 0.01;
		const geometry = new CylinderGeometry(size, size, 1, 16);
		geometry.rotateX(MathUtils.degToRad(90));
		const material = new MeshStandardMaterial({ color: "blue" });
		const cylinder = new Mesh(geometry, material);

		this.updatePositionRotationScale(cylinder, this.point1, this.point2);

		cylinder.visible = true;
		return cylinder;
	}

	update(point1: Vector3, point2: Vector3): void {
		this.point1 = point1;
		this.point2 = point2;
		this.updatePositionRotationScale(this.mesh, this.point1, this.point2);
	}

	setColor(color: ColorRepresentation): void {
		(this.mesh.material as any).color.set(color);
	}

	private updatePositionRotationScale(mesh: Mesh, point1: Vector3, point2: Vector3) {
		mesh.position.copy(point1);
		mesh.position.lerp(point2, 0.5);
		mesh.lookAt(point1);
		mesh.scale.set(1, 1, distanceTo(point1, point2));
	}
}

export { MeshLink }