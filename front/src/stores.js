import { readable } from 'svelte/store';
import { writable } from 'svelte/store';


const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

let arrayVoltage = [];
let arrayCurrent = [];
let arrayMah = [];
let arrayTime = [];
let batteryState = 0;
let batteryCapacity = 0;
let chartId = "";


async function updateData() {
  try {
    const url = `${apiUrl}/battery-state?start=${arrayVoltage.length}&id=${chartId}`;
    const response = await fetch(url);
    if (response.ok) {
      const responseData = await response.json();
      if ("chart_id" in responseData) {
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
      console.error("Failed to fetch data");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}


const initialState = {
  state: 0,
  voltage: [],
  current: [],
  mah: [],
  time: [],
  capacity: 0,
};

export const batteryData = readable(initialState, (set) => {
  const interval = setInterval(() => {
    updateData();
    let battery_data  = {
      state: batteryState,
      voltage: arrayVoltage,
      current: arrayCurrent,
      mah: arrayMah,
      time: arrayTime,
      capacity: batteryCapacity,
    }
    set(battery_data);
  }, 2000);
  return () => {
    clearInterval(interval);
  };
});


const initialParams = {
  charge_v: 4.2,
  charge_c: 1,
  discharge_v: 2.7,
  discharge_c: 1,
  n_cycles: 1,
  original_capacity: 0,
};

export const deviceParameters = writable(initialParams);