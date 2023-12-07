import { readable } from 'svelte/store';
import { writable } from 'svelte/store';


const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

let arrayVoltage = [];
let arrayCurrent = [];
let arrayMah = [];
let arrayTime = [];
let deviceState = 0;
let batteryState = 0;
let batteryCapacity = 0;
let deviceError = false;
let chartId = "";
let devops = [];


async function updateData() {
  try {
    const url = `${apiUrl}/get-state?start=${arrayVoltage.length}&id=${chartId}`;
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
      if ("device_state" in responseData) {
        deviceState = responseData.device_state;
      }
      if ("operations" in responseData) {
        devops = responseData.operations;
      }

      console.log(responseData);      
    } else {
      deviceError = true;
      console.error("Failed to fetch data");
    }
  } catch (error) {
    deviceError = true;
    console.error("Error:", error);
  }
}


const initialDeviceData = {
  battery_state: 0,
  device_error: deviceError,
  voltage: [],
  current: [],
  mah: [],
  time: [],
  capacity: 0,
  operations: [],
};

export const deviceData = readable(initialDeviceData, (set) => {
  const interval = setInterval(() => {
    updateData();
    set({
      battery_state: batteryState,
      device_state: deviceState,
      device_error: deviceError,
      voltage: arrayVoltage,
      current: arrayCurrent,
      mah: arrayMah,
      time: arrayTime,
      capacity: batteryCapacity,
      operations: devops,
    });
    console.log("device status updated");
  }, 2000);
  return () => {
    clearInterval(interval);
  };
});


const initialDeviceParams = {
  charge_v: 4.2,
  charge_c: 1,
  discharge_v: 2.7,
  discharge_c: 1,
  vmax: 4.2,
  vmin: 2.7,
  n_cycles: 1,
  original_capacity: 0,
};

export const deviceParameters = writable(initialDeviceParams);