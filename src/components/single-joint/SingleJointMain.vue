<template lang="pug">
h3 Annotating file: {{ getFileName(file) }} 
h3 Frame: {{ frame }} of {{ max_frames }}

//- make a slider from 0 to max_frames
.row
    .col-lg-3
    .col.lg-6
        .btn-group
            button.btn.btn-primary(@click="prevFrame" :disabled="frame <= 0") Previous
            button.btn.btn-secondary(@click="resetLocations") Reset Locations
            button.btn.btn-secondary(@click="getProcessed" :disabled="processed") Apply Image Preprocessing
            button.btn.btn-primary(@click="nextFrame" :disabled="frame >= max_frames") Next
    .col-lg-3
.row
    input(type="range" class="form-range" min="0" :max="max_frames" v-model="frame" step="1")

.row(v-if="file && annotation")
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
.row(v-else)
    .col
        h4 No data to show (either no 2D or 3D data).
        h4 Current file: {{ file }} 
        h4 Annotation present? {{ annotation != null }}

</template>

<script setup lang="ts">
import AnnotatorVue from './SingleJointAnnotator.vue';

import { ref, onMounted, watch, watchEffect, computed } from 'vue';
import { useRoute } from 'vue-router';
import { UriBuilder } from '@/uri';
import axios from 'axios';
import { ImageBase64 } from "@/data_structures/Image";
import { FrameAnnotation, Annotations } from '@/data_structures/Annotation';
import { useLoading } from 'vue-loading-overlay';
import type { Point2D } from '@/data_structures/Point';

let loader = useLoading();
const route = useRoute();
const file = ref<string>("");
const frame = ref<number>(0);
const currentFrame = ref<ImageBase64>();
const annotation = ref<FrameAnnotation>();
const max_frames = ref<number>(0);

const annotations = ref<Annotations>();

onMounted(() => {
    file.value = route.query.target as string;
    frame.value = parseInt(route.query.frame as string);
    get_annotation_data();
})

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

    let res = await axios.get(url.build())
    let annJson = res.data.annotations as any;
    let db = Annotations.fromJSON(annJson);
    annotations.value = db;
    let ann = db.annotations[frame.value] as FrameAnnotation;
    max_frames.value = res.data.max_frames as number;
    let base64 = res.data.frame as string;
    // let format = res.data.format as string;
    // console.log(res.data);
    let img = new ImageBase64(base64);
    currentFrame.value = img;
    annotation.value = ann;

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

watchEffect(() => {
    if (!annotations.value) {
        return;
    }
    let ann = annotations.value.annotations[frame.value] as FrameAnnotation;
    annotation.value = ann;

    let url = new UriBuilder(
        window.remoteWebServerUrl,
        "get_frame"
    )
    url.addParam("target", file.value)
    url.addParam("frame", frame.value?.toString() ?? "-1")

    axios.get(url.build()).then((res) => {
        let base64 = res.data.frame as string;
        let img = new ImageBase64(base64);
        currentFrame.value = img;
    })

})

function saveAnnotation() {
    if (!annotations.value) {
        return;
    }
    let url = new UriBuilder(
        window.remoteWebServerUrl,
        "save"
    )
    let to_save = annotations.value.toJSON();
    console.log("Saving", to_save.annotations[0].visibles);
    axios.post(url.build(), to_save).then((res) => {
        console.log("Saved successfully", res.data);
    })
}

function getFileName(file: string | undefined) {
    if (!file) {
        return "<unknown>";
    }
    // get last part of path
    let last = file.split("/").pop();
    // remote ext
    return last?.split(".")[0] ?? "<unknown>";
}

const processed = ref<boolean>(false);
async function getProcessed() {
    if (!currentFrame.value) {
        return;
    }
    let url = new UriBuilder(
        window.remoteWebServerUrl,
        "image_processing"
    )
    let response = await axios.post(url.build(), { "frame": currentFrame.value?.base64 });
    let base64 = response.data.frame as string;
    currentFrame.value.base64 = base64;
    processed.value = true;
}

function getVisibleText(pt: Point2D) {
    if (pt.visible) {
        return "visible";
    }
    return "hidden";
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
