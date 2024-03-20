<template lang="pug">

table.table.table-striped.table-hover
    thead
        tr
            //- th #
            th Name
            th Has 3D Data
            th Annotated
            th Action
    tbody
        template(v-for="(file, index) in filesToAnnotate" v-if="filesToAnnotate.length > 0" :key="index")
            //- tr(v-if="!isHidden(index)")
            tr
                //- td {{index}}
                td 
                    div(@click="open_explorer(file)" style="cursor: pointer") 
                        | {{getFileName(file)}}
                td 
                    //- i.bi.bi-x-circle-fill.red(v-if="!hasSourceData(index)")
                    //- i.bi.bi-check-circle-fill.green
                    div(v-if="!hasSourceData(index)")
                        i.bi.bi-x-circle-fill.red
                    div(v-else)
                        i.bi.bi-check-circle-fill.green
                td  
                    div(v-if="!hasAnnotation(index)")
                        i.bi.bi-x-circle-fill.red
                    div(v-else-if="isCompletelyAnnotated(index)")
                        i.bi.bi-check-circle-fill.green
                    div(v-else)
                        i.bi.bi-check-circle-fill.yellow
                td
                    button.btn.btn-primary(@click="startAnnotating(file, index)") Annotate Pose
                    //- button.btn.btn-secondary(@click="startJointAnnotating(file)") Annotate Single Joints 
                    //- button.btn.btn-secondary.ms-1(@click="hide(index)") Hide

        tr(v-else)
            td(colspan="4") No files to annotate
</template>

<script setup lang="ts">
import router from '@/router';
import { defualtUriBuilder } from '@/uri';
import { useStore } from "@/store";
import axios from 'axios';
import { onMounted, ref } from 'vue';
import { useLoading } from 'vue-loading-overlay';
import ServerFile from '@/data_structures/ServerFile';

let store = useStore();
let loader = useLoading();

const filesToAnnotate = ref<ServerFile[]>([]);
// const filesWithSourceData = ref<boolean[]>([]);
// const filesWithAnn = ref<boolean[]>([]);

onMounted(() => {
    getFiles();
})

async function getFiles() {
    const _loader = loader.show({
        // // Optional parameters
        // container: null, // fullpage
        canCancel: false,
        // onCancel: onCancel,
    });
    let url = defualtUriBuilder("list")
    try {
        let data = await axios.get(url);

        let serverData = data.data;
        let _serverFiles = serverData.files as string[];
        let _filesWithAnn = serverData.has_annotations as boolean[];
        let _filesWithSourceData = serverData.has_source_data as boolean[];

        let serverFilesObjs = [];

        for (let i = 0; i < _serverFiles.length; i++) {
            let file = _serverFiles[i];
            let hasAnn = _filesWithAnn[i];
            let hasSource = _filesWithSourceData[i];
            let serverFile = new ServerFile(file, hasAnn, hasSource);
            serverFilesObjs.push(serverFile);
        }

        // /// DEBUG ///
        // // order by camera name, located in the filename after the '--' character and before its consecutive "_"
        // serverFilesObjs.sort((a: ServerFile, b: ServerFile) => {
        //     let aCam = a.filename.split("--")[1].split("_")[0];
        //     let bCam = b.filename.split("--")[1].split("_")[0];
        //     return aCam.localeCompare(bCam);
        // });
        // // remove files without "left_fisheye_image" in the name
        // serverFilesObjs = serverFilesObjs.filter((f: ServerFile) => {
        //     return f.filename.includes("--left_fisheye_image"); // || f.filename.includes("--back_fisheye_image");
        // });
        // /////////////

        filesToAnnotate.value = serverFilesObjs;

        for (let i = 0; i < filesToAnnotate.value.length; i++) {
            store.$state.temporaryHiddenIndexes[i] = false;
        }

    } catch (e) {
        store.$state.errorMessage = "Error getting files to annotate " + e;
    }
    _loader.hide();
}

function getFileName(file: ServerFile) {
    // get last part of path
    let last = file.filename.split("/").pop();

    // remote ext
    let fname = last?.split(".")[0] ?? "<unknown>";

    return fname;
}

function hasSourceData(index: number) {
    if (!filesToAnnotate.value) {
        return false;
    }
    if (filesToAnnotate.value.length <= index) {
        return false;
    }
    return filesToAnnotate.value[index].hasSourceData;
}

function hasAnnotation(index: number) {
    if (!filesToAnnotate.value) {
        return false;
    }
    if (filesToAnnotate.value.length <= index) {
        return false;
    }
    return filesToAnnotate.value[index].hasAnnotation;
}

function isCompletelyAnnotated(index: number) {
    if (!filesToAnnotate.value) {
        return false;
    }
    if (filesToAnnotate.value.length <= index) {
        return false;
    }
    return filesToAnnotate.value[index].hasAnnotation;
}

function startAnnotating(file: ServerFile, index: number) {
    let cam = encodeURIComponent(file.filename);
    let idx = 0;
    let route = `/annotate/?target=${cam}&frame=${idx}`;
    store.$state.currFileIndex = index;
    router.push(route);
}

function startJointAnnotating(file: string) {
    let cam = encodeURIComponent(file);
    let idx = 0;
    let route = `/annotate-joints/?target=${cam}&frame=${idx}`;
    router.push(route);
}

function open_explorer(f: ServerFile) {
    let url = defualtUriBuilder("open_explorer");
    axios.post(url, { file: f.filename }).catch((e) => {
        store.$state.errorMessage = "Error opening explorer " + e;
    })
}

function hide(index: number) {
    store.$state.temporaryHiddenIndexes[index] = true;
}

function isHidden(index: number) {
    return store.$state.temporaryHiddenIndexes[index];
}

</script>


<style scoped lang="scss">
.red {
    color: red
}

.green {
    color: green
}

.yellow {
    color: yellow
}
</style>