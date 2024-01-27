<template lang="pug">

//- .container
table.table.table-striped.table-hover
    thead
        tr
            th Name
            th Has 3D Data
            th Annotated
            th Action
    tbody
        tr(v-for="(file, index) in filesToAnnotate" v-if="filesToAnnotate.length > 0" :key="index")
            td {{getFileName(file)}}
            td 
                //- i.bi.bi-x-circle-fill.red(v-if="!hasSourceData(index)")
                //- i.bi.bi-check-circle-fill.green
                div(v-if="!hasSourceData(index)")
                    | No
                div(v-else)
                    | Yes
            td  
                div(v-if="!hasAnnotation(index)")
                    | No
                div(v-else)
                    | Yes
            td
                button.btn.btn-primary(@click="startAnnotating(file)") Annotate  
        tr(v-else)
            td(colspan="4") No files to annotate
</template>

<script setup lang="ts">
import router from '@/router';
import { defualtUriBuilder } from '@/uri';
import axios from 'axios';
import { onMounted, ref } from 'vue';
import { useLoading } from 'vue3-loading-overlay';

let loader = useLoading();

const filesToAnnotate = ref<string[]>([]);
const filesWithSourceData = ref<boolean[]>([]);
const filesWithAnn = ref<boolean[]>([]);

onMounted(() => {
    getFiles();
})

async function getFiles() {
    loader.show({
        // Optional parameters
        container: null, // fullpage
        canCancel: false,
        // onCancel: onCancel,
    });
    let url = defualtUriBuilder("list")
    let data = await axios.get(url);

    let serverData = data.data;
    let serverFiles = serverData.files as string[];
    let _filesWithAnn = serverData.has_annotations as boolean[];
    let _filesWithSourceData = serverData.has_source_data as boolean[];

    filesToAnnotate.value = serverFiles;
    filesWithSourceData.value = _filesWithSourceData;
    filesWithAnn.value = _filesWithAnn;
    loader.hide();
}

function getFileName(file: string) {
    // get last part of path
    let last = file.split("/").pop();
    // remote ext
    return last?.split(".")[0] ?? "<unknown>";
}

function hasSourceData(index: number) {
    if (!filesWithSourceData.value) {
        return false;
    }
    if(filesWithSourceData.value.length <= index) {
        return false;
    }
    return filesWithSourceData.value[index];
}

function hasAnnotation(index: number) {
    if (!filesWithAnn.value) {
        return false;
    }
    if(filesWithAnn.value.length <= index) {
        return false;
    }
    return filesWithAnn.value[index];
}

function startAnnotating(file: string) {
    let cam = encodeURIComponent(file);
    let idx = 0;
    let route = `/annotate/?target=${cam}&frame=${idx}`;
    router.push(route);
}

</script>


<style scoped lang="scss">
.red {
	color: red
}

.green {
	color: green
}
</style>