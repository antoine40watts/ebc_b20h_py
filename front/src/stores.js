import { readable } from 'svelte/store';
// import { writable } from 'svelte/store';


let arrayVoltage = [];
let arrayCurrent = [];
let arrayMah = [];
let arrayTime = [];
let batteryState = 0;
let chartId = "";

async function updateData() {
  try {
    const url = `http://localhost:8000/battery-state?start=${arrayVoltage.length}&id=${chartId}`;
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
}


export const batteryData = readable(initialState, (set) => {
  const interval = setInterval(() => {
    updateData();
    let battery_data  = {
      state: batteryState,
      voltage: arrayVoltage,
      current: arrayCurrent,
      mah: arrayMah,
      time: arrayTime,
    }
    set(battery_data);
  }, 2000);
  return () => {
    clearInterval(interval);
  };
});