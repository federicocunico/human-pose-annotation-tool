<script setup lang="ts">
import { FrameAnnotation } from '@/data_structures/Annotation';
import { World } from '@/three_wrapper/World';
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { Color, Vector3 } from 'three';

const props = defineProps<{
	annotation: FrameAnnotation
}>()

onMounted(() => {
	main();
	addAnnotatedSkeleton();

	// Listen for window resize event and update renderer size
	window.addEventListener('resize', onWindowResize);
	onWindowResize();
});

onBeforeUnmount(() => {
	// Remove the event listener when the component is destroyed
	window.removeEventListener('resize', onWindowResize);
});

const container = ref<HTMLElement | null>(null);
const canvas = ref<HTMLElement | null>(null);
let world: World = null as any;

function main() {
	if (!canvas.value) {
		throw new Error("Container element not found");
	}
	world = new World(canvas.value);
	world.setUp();
	world.setCameraPosition(0, 6, 12);
	world.lookAt();
	world.enableControls(true);
}

function getColWidth() {
	if (!container.value) {
		throw new Error("Container element not found");
	}
	return container.value.offsetWidth / 3;
}

function onWindowResize() {
	console.log(getColWidth());
	// Update the renderer size on window resize
	world.camera.aspect = getColWidth() / window.innerHeight;
	world.camera.updateProjectionMatrix();
	world.renderer.setSize(getColWidth(), window.innerHeight);
}

function addAnnotatedSkeleton(selectedPoint: number = -1) {
	if (world) {
		world.clearWorld();
		let joints3d = [] as Array<Vector3>;
		for (let joint of props.annotation.joints_3d) {
			joints3d.push(new Vector3(joint.x, joint.y, joint.z));
		}
		let colors = [] as Array<Color>;
		// for (let joint of props.annotation.joints_3d) {
		// 	colors.push(new Color(1, 0, 0));
		// }
		for (let i = 0; i < props.annotation.joints_3d.length; i++) {
			if (i == selectedPoint) {
				colors.push(new Color(1, 1, 0)); // yellow
			} else {
				colors.push(new Color(1, 0, 0));
			}
		}
		world.addSkeleton(joints3d, colors, props.annotation.links_3d);
	}
}

watch(() => props.annotation, () => {
	if (!props.annotation) {
		return;
	}
	let selectedPoint = props.annotation.selectedPoint;
	addAnnotatedSkeleton(selectedPoint);  // if negative is ignored
}, { deep: true })

</script>

<template lang="pug">
//- Three js container
div(ref="container")
	canvas(ref="canvas")

</template>

<style scoped lang="scss"></style>
