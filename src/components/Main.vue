<template lang="pug">
h3 Annotating file: 
    div(@click="open_explorer(file)" style="cursor: pointer;") {{ getFileName(file) }} 
h3 Frame: {{ frame }} of {{ max_frames }}

//- make a slider from 0 to max_frames
.row
    .col-lg-3
    .col.lg-6
        .btn-group
            button.btn.btn-primary(@click="prevFrame" :disabled="frame <= 0") Previous
            button.btn.btn-secondary(@click="addJoint" :disabled="maxJointReached") Add Joint
            button.btn.btn-link(@click="debugView") Debug
            button.btn.btn-warning(@click="applyProcessing") {{ processingLabel() }}
            button.btn.btn-secondary(@click="resetLocations") Reset Locations
            button.btn.btn-secondary(@click="resetVisibility") Reset Visibility
            //- make a dropdown with all joints2d visibility checkboxes
            template(v-if="annotation")
                .btn-group
                    button.btn.btn-success.dropdown-toggle(type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false") Joint Visibility
                    ul.dropdown-menu
                        li(v-for="(pt, index) in annotation.joints_2d" :key="index" href="")
                            div.dropdown-item(
                                style="cursor: pointer;"
                                :class="pt.visible?'joint-visilbe' : 'joint-hidden'"
                                @click="setVisibility($event, index)")
                                | {{ annotation.names_2d[index] }} : {{ getVisibleText(pt) }}

            button.btn.btn-primary(@click="nextFrame" :disabled="frame >= max_frames") Next
    .col-lg-3
.row
    .col.pl-5.pr-5
        input(type="range" class="form-range" min="0" :max="max_frames" v-model="frame" step="1")

.row(v-if="file && annotation")
    .col(v-if="has3dData")
        h4 3D Data
        Plot3D(:annotation="annotation")
    .col
        h4 2D Data 
        template(v-if="currentFrame")
            AnnotatorVue(
                :image="currentFrame"
                :annotation="annotation"
                @data-updated="saveAnnotation"
            )
        template(v-else)
            h4 No frame found
        p Image Frame: {{ lastUpdatedFrame }}
.row(v-else)
    .col
        h4 No data to show (either no 2D or 3D data).
        h4 Current file: {{ file }} 
        h4 Annotation present? {{ annotation != null }}

//- debug
//- div.row
//-     | Selected: {{ annotation?.selectedPoint }}
</template>






  

<script setup lang="ts">
import AnnotatorVue from './Annotator.vue';
import Plot3D from '@/components/Plot3D.vue'

import { ref, onMounted, watch, watchEffect, computed, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { UriBuilder, defualtUriBuilder } from '@/uri';
import { useStore } from '@/store';
import axios from 'axios';
import { ImageBase64 } from "@/data_structures/Image";
import { FrameAnnotation, Annotations } from '@/data_structures/Annotation';
import { useLoading } from 'vue-loading-overlay';
import { Point2D } from '@/data_structures/Point';

let store = useStore();
let loader = useLoading();
const route = useRoute();
const file = ref<string>("");
const frame = ref<number>(0);
const currentFrame = ref<ImageBase64>();
const annotation = ref<FrameAnnotation>();
const max_frames = ref<number>(0);

const annotations = ref<Annotations>();

const isProcessingApplied = ref<boolean>(false);

let lastFrameRequest: Promise<any> | null = null;
let lastSaveRequest: Promise<any> | null = null;
let lastUpdatedFrame = ref<number>(0);
let ensureCorrectFrameInterval = 500 as number;
let ensureCorrectFrameCall = 0 as number; // setInterval id

onMounted(() => {
    file.value = route.query.target as string;
    frame.value = parseInt(route.query.frame as string);
    get_annotation_data();

    // ensureCorrectFrameCall = setInterval(() => {
    //     ensureCorrectFrame();
    // }, ensureCorrectFrameInterval);

})

onBeforeUnmount(() => {
    clearInterval(ensureCorrectFrameCall);
})

function ensureCorrectFrame() {
    if (lastUpdatedFrame.value != frame.value) {
        console.warn("Frame not updated, requesting new frame");
        requestNewFrame();
    }
}

async function get_annotation_data() {
    const _loader = loader.show({
        // Optional parameters
        // container: null, // fullpage
        canCancel: false,
        // onCancel: onCancel,
    });

    let url = new UriBuilder(
        window.remoteWebServerUrl,
        "annotation"
    )
    url.addParam("target", file.value)
    url.addParam("frame", frame.value?.toString() ?? "-1")
    try {
        let res = await axios.get(url.build())
        let annJson = res.data.annotations as any;
        let db = Annotations.fromJSON(annJson);
        annotations.value = db;
        let ann = db.annotations[frame.value] as FrameAnnotation;
        max_frames.value = res.data.max_frames as number;
        let base64 = res.data.frame as string;
        let img = new ImageBase64(base64);
        currentFrame.value = img;
        annotation.value = ann;
    }
    catch (e) {
        store.$state.errorMessage = "Error getting annotation data " + e;
    }

    _loader.hide();
}

function nextFrame() {
    if (!annotations.value) {
        return;
    }
    if (frame.value >= max_frames.value) {
        return;
    }
    frame.value += 1;
    let ann = annotations.value.annotations[frame.value] as FrameAnnotation;
    annotation.value = ann;
}

function prevFrame() {
    if (!annotations.value) {
        return;
    }
    if (frame.value <= 0) {
        return;
    }
    frame.value -= 1;
    let ann = annotations.value.annotations[frame.value] as FrameAnnotation;
    annotation.value = ann;
}

watch(() => frame.value, () => {
    if (!annotations.value) {
        return;
    }
    let ann = annotations.value.annotations[frame.value] as FrameAnnotation;
    annotation.value = ann;
    requestNewFrame();
    isProcessingApplied.value = false;
})

// watchEffect(() => {
//     if (!annotations.value) {
//         return;
//     }
//     let ann = annotations.value.annotations[frame.value] as FrameAnnotation;
//     annotation.value = ann;

//     requestNewFrame();

// })


function requestNewFrame() {
    let url = new UriBuilder(
        window.remoteWebServerUrl,
        "get_frame"
    )
    url.addParam("target", file.value)
    url.addParam("frame", frame.value?.toString() ?? "-1")

    if (lastFrameRequest != null) {
        return;
    }
    lastFrameRequest = axios.get(url.build()).then((res) => {
        let base64 = res.data.frame as string;
        let imgFrame = res.data.current_frame as number;
        let img = new ImageBase64(base64);
        currentFrame.value = img;
        lastUpdatedFrame.value = imgFrame;
    })
        .catch((e) => {
            store.$state.errorMessage = "Error getting frame " + e;
        })
        .finally(() => {
            lastFrameRequest = null;
            console.log("Resetting lastFrameRequest")
            setTimeout(() => {
                ensureCorrectFrame();
            }, ensureCorrectFrameInterval);
        })
}

function saveAnnotation() {
    if (!annotations.value) {
        return;
    }
    if (lastSaveRequest != null) {
        return;
    }
    let url = new UriBuilder(
        window.remoteWebServerUrl,
        "save"
    )
    let to_save = annotations.value.toJSON();
    lastSaveRequest = axios.post(url.build(), to_save)
        .catch((e) => {
            store.$state.errorMessage = "Error saving annotation " + e;
        })
        .finally(() => {
            lastSaveRequest = null;
        })
}

function processingLabel() {
    // {{ isProcessingApplied ? 'Remove Processing' : 'Apply Processing' }}
    if (isProcessingApplied.value) {
        return "Processing (On)";
    }
    return "Processing (Off)";
}

function getFileName(file: string | undefined) {
    if (!file) {
        return "<unknown>";
    }
    // // get last part of path
    // let last = file.split("/").pop();
    // // remote ext
    // return last?.split(".")[0] ?? "<unknown>";
    return file;
}

function setVisibility(event: MouseEvent, index: number) {
    event.preventDefault();
    if (annotations.value == null) {
        return;
    }
    if (annotation.value === undefined) {
        return;
    }
    let pt = annotation.value?.joints_2d[index];
    annotation.value.joints_2d[index].visible = !pt.visible;
}

function getVisibleText(pt: Point2D) {
    if (pt.visible) {
        return "visible";
    }
    return "hidden";
}

function resetVisibility() {
    let answer = confirm("Are you sure you want to reset visibility?");
    if (!answer) {
        return;
    }

    if (!annotations.value) {
        return;
    }
    annotation.value?.resetVisibility();
}


function resetLocations() {
    let answer = confirm("Are you sure you want to reset locations? This action is NOT reversable");
    if (!answer) {
        return;
    }

    if (!annotations.value) {
        return;
    }
    annotation.value?.resetLocations();
}

const has3dData = computed(() => {
    if (!annotation.value) {
        return false;
    }
    return annotation.value.has3dData();
})


function addJoint() {
    if (!annotation.value) {
        return;
    }
    if (maxJointReached()) {
        return
    }
    annotation.value.joints_2d.push(new Point2D(
        120,
        120,
        false,
        1,
    ));
}

function maxJointReached() {
    if (!annotation.value) {
        return false;
    }
    let pts = annotation.value.joints_2d;
    if (pts.length >= annotation.value.num_joints) {
        return true;
    }
    return false;
}

function debugView() {
    let url = new UriBuilder(
        window.remoteWebServerUrl,
        "debug_plot"
    )
    url.addParam("target", file.value)
    url.addParam("frame", frame.value?.toString() ?? "-1")

    axios.get(url.build()).catch((e) => {
        store.$state.errorMessage = "Error getting debug plot " + e;
    })
}


function open_explorer(file: string) {
    let url = defualtUriBuilder("open_explorer");
    axios.post(url, { file: file }).catch((e) => {
        store.$state.errorMessage = "Error opening explorer " + e;
    })
}

function applyProcessing() {
    if (currentFrame.value == null) {
        return;
    }
    if (isProcessingApplied.value) {
        requestNewFrame();
        isProcessingApplied.value = false;
    }
    else {
        let url = new UriBuilder(
            window.remoteWebServerUrl,
            "image_processing"
        )

        axios.post(url.build(), currentFrame.value).then((res) => {
            let base64 = res.data.frame as string;
            let img = new ImageBase64(base64);
            currentFrame.value = img;
            isProcessingApplied.value = true;
        })
    }
}


</script>

<style scoped lang="scss">
.joint-visilbe {
    color: green;
    // text bold
    font-weight: bold;
}

.joint-hidden {
    color: red;
    // text bold
    font-weight: bold;
}
</style>
