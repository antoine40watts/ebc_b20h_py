import { readable } from 'svelte/store';
import { writable } from 'svelte/store';


const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

let arrayVoltage = [];
let arrayCurrent = [];
let arrayMah = [];
let arrayTime = [];
let deviceState = 0;
let batteryState = 0;
let batteryVoltage = 0;
let batteryCurrent = 0;
let batteryMah = 0;
let batteryCapacity = 0;
let deviceError = false;
let chartId = "";
let operations = [];


export async function updateData() {
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
      // responseData.chart_data.forEach((element) => {
      //   arrayVoltage = [...arrayVoltage, element.v];
      //   arrayCurrent = [...arrayCurrent, element.c];
      //   arrayMah = [...arrayMah, element.mah];
      //   arrayTime = [...arrayTime, element.t];
      // });
      deviceState = responseData.device_state
      batteryState = responseData.battery_state;
      batteryVoltage = responseData.battery_voltage;
      batteryCurrent = responseData.battery_current;
      batteryMah = responseData.battery_mah;
      batteryCapacity = responseData.battery_capacity;
      operations = responseData.operations;

      // Chart
      arrayVoltage = [];
      arrayCurrent = [];
      arrayMah = [];
      arrayTime = [];
      operations.forEach((op) => {
        op.chart.forEach((datapoint) => {
          arrayVoltage = [...arrayVoltage, datapoint[1]];
          arrayCurrent = [...arrayCurrent, datapoint[2]];
          arrayMah = [...arrayMah, datapoint[3]];
          arrayTime = [...arrayTime, datapoint[0]];
        })
      })

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


const initialDeviceState = {
  battery_state: 0,
  device_state: deviceState,
  device_error: deviceError,
  voltage_array: [],
  current_array: [],
  mah_array: [],
  time_array: [],
  voltage: batteryVoltage,
  current: batteryCurrent,
  mah: batteryMah,
  capacity: batteryCapacity,
  operations: [],
};

export const deviceData = readable(initialDeviceState, (set) => {
  const interval = setInterval(() => {
    updateData();
    set({
      battery_state: batteryState,
      device_state: deviceState,
      device_error: deviceError,
      voltage_array: arrayVoltage,
      current_array: arrayCurrent,
      mah_array: arrayMah,
      time_array: arrayTime,
      voltage: batteryVoltage,
      current: batteryCurrent,
      mah: batteryMah,
      capacity: batteryCapacity,
      operations: operations,
    });
  }, 2000);
  return () => {
    clearInterval(interval);
  };
});


const initialDeviceParams = {
  charge_v: 29.4,
  charge_c: 4,
  discharge_v: 18.9,
  discharge_c: 4,
  cells_s: 7,
  original_capacity: 0, // milliamps
};

export const deviceParameters = writable(initialDeviceParams);