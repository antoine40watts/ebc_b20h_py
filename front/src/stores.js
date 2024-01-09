import { readable } from 'svelte/store';
import { writable } from 'svelte/store';


const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

let arrayVoltage = [];
let arrayCurrent = [];
let arrayMah = [];
let arrayTime = [];
let batteryState = 0;
let batteryCapacity = 0;
let deviceError = false;
let chartId = "";


async function updateData() {
  try {
    const url = `${apiUrl}/battery-state?start=${arrayVoltage.length}&id=${chartId}`;
    const response = await fetch(url);
    if (response.ok) {
      deviceError = false;
      const responseData = await response.json();
      if ("chart_id" in responseData) {
        // Reset chart data
        chartId = responseData.chart_id;
        arrayVoltage = [];
        arrayCurrent = [];
        arrayMah = [];
        arrayTime = [];
      }
      responseData.data.forEach((element) => {
        arrayVoltage = [...arrayVoltage, element.v];
        arrayCurrent = [...arrayCurrent, element.c];
        arrayMah = [...arrayMah, element.mah];
        arrayTime = [...arrayTime, element.t];
      });
      batteryState = responseData.battery_state;
      if ("battery_capacity" in responseData) {
        batteryCapacity = responseData.battery_capacity;
      }
      
    } else {
      deviceError = true;
      console.error("Failed to fetch data");
    }
  } catch (error) {
    deviceError = true;
    console.error("Error:", error);
  }
}


const initialDeviceState = {
  battery_state: 0,
  device_error: deviceError,
  voltage: [],
  current: [],
  mah: [],
  time: [],
  capacity: 0,
};

export const deviceData = readable(initialDeviceState, (set) => {
  //console.log("Subscribed to 'deviceData' store")
  const interval = setInterval(() => {
    updateData();
    let deviceData  = {
      battery_state: batteryState,
      device_error: deviceError,
      voltage: arrayVoltage,
      current: arrayCurrent,
      mah: arrayMah,
      time: arrayTime,
      capacity: batteryCapacity,
    }
    set(deviceData);
  }, 2000);
  return () => {
    clearInterval(interval);
    //console.log("Unsubscribed from 'deviceData' store")
  };
});


const initialDeviceParams = {
  charge_v: 16.8,
  charge_c: 1,
  discharge_v: 10.8,
  discharge_c: 1,
  cells_s: 4,
  n_cycles: 1,
  original_capacity: 0, // milliamps
};

export const deviceParameters = writable(initialDeviceParams);