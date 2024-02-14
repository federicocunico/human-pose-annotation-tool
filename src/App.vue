
<template lang="pug">
h1(@click="goHome").clickable-h1 Human Pose Annotation Tool
div.alert.alert-danger.alert-dismissible.fade.show.error-visible(role="alert" v-if="thereIsError()")
  strong Error: 
  | {{ getErrorMessage() }}
  button.btn.close(type="button" data-dismiss="alert" aria-label="Close" @click="resetError")
    span(aria-hidden="true") &times;

router-view
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useStore } from "@/store";
import axios from "axios";
import { useRouter } from "vue-router";
import { defualtUriBuilder } from "./uri";

const store = useStore()
const router = useRouter();

onMounted(() => {
  // if "remote_url" in window.remoteWebServerUrl: then replace with remote_url
  // check if window.remoteWebServerUrl is in the form of ip:port or just ip

  const remoteWebServerUrl = window.remoteWebServerUrl;

  // if (window.remoteWebServerUrl.includes("remote_url")) {
  if (!isValidFormat(remoteWebServerUrl)) {
    let addr = "localhost"
    let port = "51100"
    let defaultUrl = addr + ":" + port;
    window.remoteWebServerUrl = defaultUrl;
    console.log("Runnin off-backend, updated server address")
  }
  console.log("Server Location:", window.remoteWebServerUrl)
})

function thereIsError() {
  return store.$state.errorMessage !== null;
}

function resetError() {
  store.$state.errorMessage = null;
}

function getErrorMessage() {
  return store.$state.errorMessage;
}

const isValidFormat = (url: string | undefined): boolean => {
  if (!url) {
    return false; // undefined
  }

  // Define a regular expression for the desired format: ip:port or just ip
  const regex = /^(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?$/;

  return regex.test(url);
};


function goHome() {
  router.push("/")
}

</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.clickable-h1 {
  cursor: pointer;
  transition: color 0.3s ease;
  /* Add a smooth transition for the color change */
}

.clickable-h1:hover {
  color: #0073ff;
  /* Change this to your desired highlight color */
}

.error-visible {
  position: fixed;
}
</style>


