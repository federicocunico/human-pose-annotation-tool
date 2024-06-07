<template lang="pug">
//- div 
//-     input(type="checkbox" v-model="useCircles")
.row(v-if="image.base64 != null" :style="`min-height:${containerHeight}px`")
    .col
        div(style="position: relative;")
            div(style="position: absolute; z-index: 1;")
                img(
                    ref="cameraImage" 
                    :src="'data:image/png;base64,' + image.base64"
                    style="object-fit: none;"
                )
            div(style="position: absolute; z-index: 2;")
                svg(
                    style="padding: 0;"
                    ref="SVGOverlay"
                    @mouseup="disableDrag"
                    @mousemove="onMouseMove($event)"
                    @contextmenu="onCanvasRightClick($event)"
                ).svgContainer        
                    g
                        template(v-for="l in annotation.links_2d" :key="l" v-if="showLinks")
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
                                g.hoverable-circle(

                                )
                                    circle(
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
                                    line(
                                        :x1="p.x - circleRadius"
                                        :y1="p.y"
                                        :x2="p.x + circleRadius"
                                        :y2="p.y"
                                        stroke="red"
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
                                        stroke="red"
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
.row
    ul
        li
            p Joint links: {{ showLinks? 'enabled' : 'disabled' }} (use right click to show options)
        li
            p # Joint visible {{ annotation.joints_2d.filter(j => j.visible).length }} / {{ annotation.joints_2d.length }}
</template>


<script lang="ts" setup>
import { ref, defineProps, defineEmits, onMounted, onUnmounted, nextTick, watchEffect, computed, watch } from "vue";
import { Point2D } from "@/data_structures/Point";
import { FrameAnnotation } from "@/data_structures/Annotation";
import type ImageBase64 from "@/data_structures/Image";
import ContextMenu from '@imengyu/vue3-context-menu'

const emit = defineEmits(['data-updated'])
const props = defineProps<{
    image: ImageBase64,
    annotation: FrameAnnotation
}>()

const showLinks = ref(false);
const SVGOverlay = ref<SVGElement>();
const cameraImage = ref<HTMLImageElement>();
const imageContainer = ref<HTMLDivElement>();
const maxZoom = 5;
const zoomValue = ref(1);

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

watch(() => ({ ...props.annotation }), (_new, _old) => {
    if (_old.frame != _new.frame) {
        // console.log("Frame changed, resetting zoom")
        // no need to save again
    } else {
        // NOT WORKING WITH {deep:true}
        // console.log(" Checking!")
        // for (let i =0; i < _new.joints_2d.length; i++){
        //     let currJ2d = _new.joints_2d[i];
        //     let oldJ2d = _old.joints_2d[i];
        //     if (!currJ2d.equals(oldJ2d)){
        //         console.log(" Saving!")
        //         emitSave();
        //         break
        //     }
        // }
        emitSave();
    }
}, { deep: true })


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
        p.resetOpacity();
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
    let newX = e.clientX - offsetX; //  - circleRadius * 2;
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
    // d3.select(SVGOverlay.value)
    //     .attr("width", containerWidth.value)
    //     .attr("height", containerHeight.value);
    SVGOverlay.value.style.width = containerWidth.value + "px";
    SVGOverlay.value.style.height = containerHeight.value + "px";
}

function onOptions(e: MouseEvent, idx: number) {
    //prevent the browser's default menu
    e.preventDefault();
    //show your menu
    ContextMenu.showContextMenu({
        x: e.x,
        y: e.y,
        items: [
            // {
            //     label: "Joint: " + props.annotation.names_2d[idx],
            //     divided: true,
            //     disabled: true
            // },
            {
                label: "Joint name: " + props.annotation.names_2d[idx] + " (click to edit)",
                // disabled: true,
                onClick: () => {
                    // text prompt
                    let newJointName = prompt("Enter new name for joint:", props.annotation.names_2d[idx]);
                    if (newJointName != null) {
                        props.annotation.names_2d[idx] = newJointName;
                        emitSave()
                    }
                }
            },

            {
                divided: true,
                label: "Hide Joint " + props.annotation.names_2d[idx],
                onClick: () => {
                    props.annotation.joints_2d[idx].visible = false;
                    props.annotation.visibles[idx] = false;  // need to update visibles too, don't know why
                }
            },
            {
                label: "Show links",
                onClick: () => {
                    showLinks.value = true;
                }
            },
            {
                label: "Hide links",
                onClick: () => {
                    showLinks.value = false;
                }
            }
        ]
    });
}

function emitSave(){
    emit("data-updated");
}

function onCanvasRightClick(e: MouseEvent) {
    // if click is over a joint, do nothing
    // let mousePos = getImageMousePosition(e);
    // if (mousePos == null) return;
    // let newX = mousePos.x;
    // let newY = mousePos.y;

    // for (let p of props.annotation.joints_2d) {
    //     let dist = Math.pow(p.x - newX, 2) + Math.pow(p.y - newY, 2);
    //     if (dist < Math.pow(circleRadius, 2)) {
    //         return;
    //     }
    // }
    if (props.annotation.selectedPoint >= 0) {
        return;
    }

    // otherwise, show options and prevent default context menu
    e.preventDefault();

    ContextMenu.showContextMenu({
        x: e.x,
        y: e.y,
        items: [
            // {
            //     label: "Zoom In",
            //     // disabled: true,
            //     onClick: () => {
            //         doZoom(e, true);
            //     }
            // },
            // {
            //     label: "Zoom Out",
            //     // disabled: true,
            //     onClick: () => {
            //         doZoom(e, false);
            //     }
            // },
            {
                label: "Show every joint",
                onClick: () => {
                    props.annotation.joints_2d.forEach(j => j.visible = true);
                }
            },
            {
                label: "Hide every joint",
                onClick: () => {
                    props.annotation.joints_2d.forEach(j => j.visible = false);
                }
            }
        ]
    })

}

function linkOpacity(link: Array<number>) {
    let from = link[0];
    let to = link[1];
    let opacityJ1 = props.annotation.joints_2d[from].opacity;
    let opacityJ2 = props.annotation.joints_2d[to].opacity;
    let op = Math.min(opacityJ1, opacityJ2);
    if (op == 1) {
        return 0.5;
    }
    return op;
}


// function doZoom(event: MouseEvent, zoomIn: boolean) {
//     if (!cameraImage.value || !imageContainer.value) return;

//     const img = cameraImage.value;
//     const rect = img.getBoundingClientRect();
//     const x = (event.clientX - rect.left) / rect.width;
//     const y = (event.clientY - rect.top) / rect.height;

//     let scale = parseFloat(img.style.transform.replace("scale(", "").split(")")[0]) || 1;

//     if (zoomIn) {
//         scale += 1;
//         if (scale > maxZoom) scale = maxZoom;
//     } else {
//         scale -= 1;
//         if (scale < 1) scale = 1;
//     }

//     img.style.transformOrigin = `${x * 100}% ${y * 100}%`;
//     img.style.transform = `scale(${scale})`;
// }
function doZoom(event: MouseEvent, zoomIn: boolean) {
    if (!cameraImage.value || !imageContainer.value || !SVGOverlay.value) return;

    const img = cameraImage.value;
    const rect = img.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width;
    const y = (event.clientY - rect.top) / rect.height;

    let scale = parseFloat(img.style.transform.replace("scale(", "").split(")")[0]) || 1;

    if (zoomIn) {
        scale += 1;
        if (scale > maxZoom) scale = maxZoom;
    } else {
        scale -= 1;
        if (scale < 1) scale = 1;
    }
    zoomValue.value = scale;

    img.style.transformOrigin = `${x * 100}% ${y * 100}%`;
    img.style.transform = `scale(${scale})`;

    // Apply the same scale transformation to the SVG container
    SVGOverlay.value.style.transform = `scale(${scale})`;
}

</script>

<style lang="scss">
$image-height: 500px;

.hoverable-circle:hover {
    cursor: pointer;
    stroke-width: 1px;
    stroke: yellow;
}

.rowContainer {
    /* position: relative;
    display: block;
    user-select: none; */
    min-height: $image-height;
}

.svgContainer {
    position: absolute;
}
</style>