<template lang="pug">

.row(v-if="image.base64 != null").rowContainer
    img(ref="cameraImage" :src="'data:image/png;base64,' + image.base64").imageContainer
    //- @mousedown="addJoint"
    svg(
        ref="SVGOverlay"
        @mouseup="disableDrag"
        @mousemove="onMouseMove($event)"
    ).svgContainer
        g
            template(v-for="l in annotation.links_2d"  :key="l")
                line(
                    v-if="isLinkShowable(l)"
                    :x1="annotation.joints_2d[l[0]].x" 
                    :y1="annotation.joints_2d[l[0]].y" 

                    :x2="annotation.joints_2d[l[1]].x" 
                    :y2="annotation.joints_2d[l[1]].y"

                    style="stroke:rgb(255,0,0);stroke-width:2"
                )
        g
            circle.hoverable-circle(
                v-for="p in annotation.joints_2d"
                :cx="p.x"
                :cy="p.y"
                :r="circleRadius"
                fill="blue"
                @mousedown="enableDrag(p)"
                @mouseleave="onMouseLeave"
                @mouseenter="onMousEnter"
            )
            g(v-for="(p, index) in annotation.joints_2d" :key="index")
                text(
                    :x="p.x-10" 
                    :y="p.y" 
                    font-size="16px"
                    font-weight="bold"
                    text-anchor="middle"
                    fill="blue"
                    stroke="black"
                    stroke-width="1px"
                    ) {{ (annotation.names_2d[index]) }}

            
</template>


<script lang="ts" setup>
import { ref, defineProps, defineEmits, onMounted, nextTick, watchEffect, computed, watch } from "vue";
import { Point2D } from "@/data_structures/Point";
import * as d3 from "d3";
import { FrameAnnotation } from "@/data_structures/Annotation";
import type ImageBase64 from "@/data_structures/Image";

const emit = defineEmits(['data-updated'])
const props = defineProps<{
    image: ImageBase64,
    annotation: FrameAnnotation
}>()

const SVGOverlay = ref<SVGElement>();
const cameraImage = ref<HTMLImageElement>();

const containerWidth = ref(0);
const containerHeight = ref(0);

const imageWidth = ref(0);
const imageHeight = ref(0);

const circleRadius = 6;

// onMounted(() => {
//     // const svg = d3.select(svgElement.value);
//     // const svg = d3.select(svgElement.value as any);
//     // setOverOnKeypoints(svg);
// });

onMounted(() => {
    window.onresize = onResize;

    nextTick(() => {
        onResize();
        // setTimeout(() => {
        //     applyPts();
        // }, 0.1)
    })
})


watchEffect(() => {
    let img = new Image();
    img.src = "data:image/png;base64," + props.image.base64;
    img.onload = () => {
        imageWidth.value = img.width;
        imageHeight.value = img.height;
    }
})

const currentDraggingPoint = ref<Point2D | null>(null);

watch(() => props.annotation.joints_2d, (_new, _old) => {
    emit("data-updated", props.annotation);
}, { deep: true })

// const calibrationPoints = ref<Point[]>([
//     { x: 10, y: 10 },
//     { x: 10, y: 20 },
//     { x: 20, y: 20 },
//     { x: 20, y: 10 }
// ]);
// const controlPointsSvg = ref<Point[]>([]);

// // const controlPoints = ref<Point[]>([]);

// // function setOverOnKeypoints(svg: d3.Selection<any, unknown, null, undefined>) {
// //     svg.selectAll("circle")
// //         .on("mouseover", function (d) {
// //             d3.select(this)
// //                 .style("cursor", "pointer")
// //                 .attr("stroke", "yellow")
// //                 .style("stroke-width", "2px");
// //         })
// //         .on("mouseout", function (d) {
// //             let tmp = d3.select(this);
// //             tmp.style("cursor", "default").attr("stroke", "transparent");
// //         })
// // }

// watch(() => props.controlPoints, (_new, _old) => {
//     if (!props.controlPointsEnabled) {
//         let newPts = imageToPoint(props.controlPoints);
//         console.log("Setting control points", newPts)
//         controlPointsSvg.value.splice(0, controlPointsSvg.value.length, ...newPts);
//     }
// }, { deep: true })

// watch(() => controlPointsSvg.value, (_new, _old) => {
//     if (!props.controlPointsEnabled) {
//         return;
//     }
//     let newPts = pointToImage(controlPointsSvg.value);
//     props.controlPoints.splice(0, props.controlPoints.length, ...newPts);
// }, { deep: true })

// watch(() => props.frameb64, (_new, _old) => {
//     if (props.frameb64 == null) {
//         return;
//     }
//     onResize();
// })

// watch(() => calibrationPoints.value, (_new, _old) => {
//     onResize();

//     if (props.frameb64 == null) {
//         return;
//     }
//     applyPts();
// }, { deep: true })

// function imageToPoint(points: Array<Array<number>>) {
//     let newPts = Array<Point>();
//     for (let p of points) {
//         let currPoint = p[0] as any;
//         console.log("Applying pts", currPoint[0], currPoint[1], "Container width", containerWidth.value, "Image width", imageWidth.value)
//         let imageX = currPoint[0] / imageWidth.value * containerWidth.value;
//         let imageY = currPoint[1] / imageHeight.value * containerHeight.value;
//         newPts.push({ x: imageX, y: imageY });
//     }
//     return newPts;
// }

function pointToImage(points: Point2D[]) {
    // console.log("Applying pts", "Container width", containerWidth.value, "Image width", imageWidth.value)
    let newPts = Array<Array<number>>();
    for (let p of points) {
        let imageX = p.x / containerWidth.value * imageWidth.value;
        let imageY = p.y / containerHeight.value * imageHeight.value;
        newPts.push([imageX, imageY]);
    }
    return newPts;
}

// function applyPts() {
//     let newPts = pointToImage(calibrationPoints.value)
//     // clear props.pts
//     props.pts.splice(0, props.pts.length, ...newPts);
// }

function disableDrag() {
    // console.log("Disabling drag")
    currentDraggingPoint.value = null;
}

function enableDrag(point: Point2D) {
    // onResize();  // to allow correct sizes, per sicurezza resizo
    // console.log("Enabling drag")
    currentDraggingPoint.value = point;
}

function onMousEnter(e: MouseEvent) {

    // convert mouse position to image position
    let mousePos = getImageMousePosition(e);
    if (mousePos == null) return;
    let newX = mousePos.x;
    let newY = mousePos.y;

    // console.log("Mouse enter")
    let closestIndex = -1;
    let closestDistance = Number.MAX_VALUE;
    for (let i = 0; i < props.annotation.joints_2d.length; i++) {
        let p = props.annotation.joints_2d[i];
        // let dist = Math.sqrt(Math.pow(p.x - newX, 2) + Math.pow(p.y - newY, 2));
        let dist = Math.pow(p.x - newX, 2) + Math.pow(p.y - newY, 2);
        if (dist < closestDistance) {
            closestDistance = dist;
            closestIndex = i;

            console.log("Closest index", closestIndex)
            console.log("Closest distance", closestDistance)
        }
    }
    if (closestIndex == -1) {
        return;
    }
    props.annotation.setSelected(closestIndex);

    console.log("Closest index", closestIndex)
}
function onMouseLeave(e: MouseEvent) {
    // console.log("Mouse leave")
    props.annotation.unsetSelected();
}

function getImageMousePosition(e: MouseEvent) {
    let rects = SVGOverlay.value?.getClientRects();
    if (rects?.length != 1) {
        console.error("Expected one client rect");
        return;
    }
    let rect = rects[0];
    const offsetX = rect.x ?? 0;
    const offsetY = rect.y ?? 0;
    let newX = e.clientX - offsetX - circleRadius * 2;
    let newY = e.clientY - offsetY;

    return { x: newX, y: newY }
}

function onMouseMove(e: MouseEvent) {
    if (currentDraggingPoint.value == null) return;

    let mousePos = getImageMousePosition(e);
    if (mousePos == null) return;
    let newX = mousePos.x;
    let newY = mousePos.y;

    let point = currentDraggingPoint.value;
    point.x = newX;
    point.y = newY;
}

function isLinkShowable(link: Array<number>) {
    let from = link[0];
    let to = link[1];
    if (from >= props.annotation.joints_2d.length || to >= props.annotation.joints_2d.length) {
        return false;
    }
    return true;
}

// const linksDefinitions = ref([[0, 1], [1, 2], [2, 3], [3, 0]]);

// const makeLinks = computed(() => {
//     return linksDefinitions.value.map(([p1, p2]) => {
//         return { x1: calibrationPoints.value[p1].x, y1: calibrationPoints.value[p1].y, x2: calibrationPoints.value[p2].x, y2: calibrationPoints.value[p2].y }
//     });
// });



function onResize() {
    if (props.image == null || cameraImage.value == null || SVGOverlay.value == null) {
        return;
    }
    // console.log("working? ",cameraImage.value.width, cameraImage.value.height)
    // console.log(cameraImage.value.getClientRects(), cameraImage.value.getBoundingClientRect())
    let h = cameraImage.value.height;
    let w = cameraImage.value.width;
    containerWidth.value = w;
    containerHeight.value = h;
    d3.select(SVGOverlay.value)
        .attr("width", containerWidth.value)
        .attr("height", containerHeight.value);
}

// function addControlPointToggle() {
//     // controlPoints.value.push({ x: 50, y: 50 })
//     // console.log(controlPoints.value)
//     isAddingControlPoint.value = !isAddingControlPoint.value;
// }

// function addControlPoint(e: MouseEvent) {
//     if (!props.controlPointsEnabled) { return; }
//     if (!isAddingControlPoint.value) {
//         return;
//     }

//     // add point where mouse is
//     let rects = SVGOverlay.value?.getClientRects();
//     if (rects?.length != 1) {
//         console.error("Expected one client rect");
//         return;
//     }
//     let rect = rects[0];
//     const offsetX = rect.x ?? 0;
//     const offsetY = rect.y ?? 0;
//     let newX = e.clientX - offsetX - circleRadius * 2;
//     let newY = e.clientY - offsetY;
//     controlPointsSvg.value.push({ x: newX, y: newY })
// }

function addJoint(e: MouseEvent) {

    // add point where mouse is
    let rects = SVGOverlay.value?.getClientRects();
    if (rects?.length != 1) {
        console.error("Expected one client rect");
        return;
    }
    let rect = rects[0];
    const offsetX = rect.x ?? 0;
    const offsetY = rect.y ?? 0;
    let newX = e.clientX - offsetX - circleRadius * 2;
    let newY = e.clientY - offsetY;
    props.annotation.joints_2d.push({ x: newX, y: newY })
}

</script>

<style>
.hoverable-circle:hover {
    cursor: pointer;
    stroke-width: 2px;
    stroke: yellow;
}

.rowContainer {
    position: relative;
    display: block;
    user-select: none;
}

.svgContainer {
    position: absolute;
}



.imageContainer {
    width: 100%;
    /* display: block; */
    height: 100%;
}
</style>