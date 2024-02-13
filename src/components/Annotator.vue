<template lang="pug">
//- div 
//-     input(type="checkbox" v-model="useCircles")
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

                    :stroke-opacity="linkOpacity(l)"

                    style="stroke:rgb(255,0,0);stroke-width:2"
                )
        g
            template(v-for="(p, index) in annotation.joints_2d" :key="index")
                template(v-if="p.visible")

                    template(v-if="!useCircles")
                        circle.hoverable-circle(
                            :cx="p.x"
                            :cy="p.y"
                            :r="circleRadius"
                            :fill-opacity="p.opacity"
                            fill="green"
                            @mousedown="enableDrag(p)"
                            @mouseleave="onMouseLeave"
                            @mouseenter="onMousEnter"
                            @contextmenu="onOptions($event, index)"
                        )
                    template(v-else)
                        circle.hoverable-circle(
                            :cx="p.x"
                            :cy="p.y"
                            fill="none"
                        )
                        line(
                            :x1="p.x - circleRadius"
                            :y1="p.y"
                            :x2="p.x + circleRadius"
                            :y2="p.y"
                            stroke="green"
                            stroke-width="2"
                            :stroke-opacity="p.opacity"
                            @mousedown="enableDrag(p)"
                            @mouseleave="onMouseLeave"
                            @mouseenter="onMousEnter"
                            @contextmenu="onOptions($event, index)"
                        )
                        //- <!-- Vertical line -->
                        line(
                            :x1="p.x"
                            :y1="p.y - circleRadius"
                            :x2="p.x"
                            :y2="p.y + circleRadius"
                            stroke="green"
                            stroke-width="2"
                            :stroke-opacity="p.opacity"
                            @mousedown="enableDrag(p)"
                            @mouseleave="onMouseLeave"
                            @mouseenter="onMousEnter"
                            @contextmenu="onOptions($event, index)"
                        )
                    g
                        text(
                            :x="p.x -circleRadius-10" 
                            :y="p.y" 
                            font-size="16px"
                            font-weight="bold"
                            text-anchor="middle"
                            fill="green"
                            stroke="black"
                            stroke-width="1px"
                            @mousedown="enableDrag(p)"
                            @mouseleave="onMouseLeave"
                            @mouseenter="onMousEnter"
                            ) {{ (annotation.names_2d[index]) }}

</template>


<script lang="ts" setup>
import { ref, defineProps, defineEmits, onMounted, nextTick, watchEffect, computed, watch } from "vue";
import { Point2D } from "@/data_structures/Point";
import * as d3 from "d3";
import { FrameAnnotation } from "@/data_structures/Annotation";
import type ImageBase64 from "@/data_structures/Image";
import ContextMenu from '@imengyu/vue3-context-menu'

const emit = defineEmits(['data-updated'])
const props = defineProps<{
    image: ImageBase64,
    annotation: FrameAnnotation
}>()

const useCircles = ref(true);
const SVGOverlay = ref<SVGElement>();
const cameraImage = ref<HTMLImageElement>();

const containerWidth = ref(0);
const containerHeight = ref(0);

const imageWidth = ref(0);
const imageHeight = ref(0);

const circleRadius = 3;

onMounted(() => {
    window.onresize = onResize;

    nextTick(() => {
        onResize();
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
    // emit("data-updated", props.annotation);
    emit("data-updated");
}, { deep: true })
// watchEffect(() => {
//     emit("data-updated");
// })


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

            // console.log("Closest index", closestIndex)
            // console.log("Closest distance", closestDistance)
        }
    }
    if (closestIndex == -1) {
        return;
    }
    props.annotation.setSelected(closestIndex);

    // console.log("Closest index", closestIndex)
}
function onMouseLeave(e: MouseEvent) {
    // console.log("Mouse leave")
    props.annotation.unsetSelected();

    // resets opacities
    for (let p of props.annotation.joints_2d) {
        p.opacity = 1;
    }
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
    point.opacity = 0.5;
}

function isLinkShowable(link: Array<number>) {
    let from = link[0];
    let to = link[1];
    if (from >= props.annotation.joints_2d.length || to >= props.annotation.joints_2d.length) {
        return false;
    }
    if (!props.annotation.joints_2d[from].visible || !props.annotation.joints_2d[to].visible) {
        return false;
    }

    return true;
}


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

function onOptions(e: MouseEvent, idx: number) {
    //prevent the browser's default menu
    e.preventDefault();
    //show your menu
    ContextMenu.showContextMenu({
        x: e.x,
        y: e.y,
        items: [
            {
                label: "Joint: " + props.annotation.names_2d[idx],
                divided: true,
                disabled: true
            },

            {
                label: "Hide",
                onClick: () => {
                    props.annotation.joints_2d[idx].visible = false;
                    props.annotation.visibles[idx] = false;  // need to update visibles too, don't know why
                }
            }
        ]
    });
}

function linkOpacity(link: Array<number>) {
    let from = link[0];
    let to = link[1];
    let opacityJ1 = props.annotation.joints_2d[from].opacity;
    let opacityJ2 = props.annotation.joints_2d[to].opacity;
    return Math.min(opacityJ1, opacityJ2);
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