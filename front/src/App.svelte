<script>
  import { deviceParameters, apiUrl } from "./stores.js";
  import { tick } from "svelte";

  import ClientPanel from "./lib/ClientPanel.svelte";
  import BatteryPanel from "./lib/BatteryPanel.svelte";
  import DiagPanel from "./lib/DiagPanel.svelte";

  // import IDBar from "./lib/IDBar.svelte";
  import BattState from "./lib/BattState.svelte";
  import BattChart from "./lib/BattChart.svelte";
  // import BattCapacity from "./lib/BattCapacity.svelte";
  // import BattControl from "./lib/BattControl.svelte";
  import BattControl2 from "./lib/BattControl2.svelte";
  import ErrorModal from './lib/ErrorModal.svelte';

  import logo from "./assets/logo-40Watts.png";

  let cells_s = 1;
  let cells_p = 1;
  let cell_cap = 3200;

  let client_panel_open = false;
  let battery_panel_open = false;


  function updateParams() {
    deviceParameters.update((params) => {
        params.charge_v = Math.round(4.2 * cells_s * 100) / 100;
        params.discharge_v = Math.round(2.7 * cells_s * 100) / 100;
        params.original_capacity = Math.round(cell_cap * cells_p);
        return params;
    });
  }

  let csvFileName = "battery_data.csv";
  let jsonFileName = "battery_data.json";

  function downloadRaw() {
      let url = apiUrl + "/battery-state";
      window.open(url, '_blank');
  }

  function downloadCSV() {
      let url = apiUrl + "/get-csv?filename=" + csvFileName;
      window.open(url, '_blank');
  }

  function printPage() {
    client_panel_open = true;
    battery_panel_open = true;
    tick();

    setTimeout(() => window.print(), 200);
  }

  function getDate() {
    var currentDate = new Date();
    var year = currentDate.getFullYear();
    var month = currentDate.getMonth() + 1; // Month is zero-based, so add 1
    var day = currentDate.getDate();

    return day + '-' + month + '-' + year;
  }

</script>


<main>
  <!-- <IDBar /> -->

  <div class="hide-on-screen print-header">
    <img src={logo} alt="Logo 40Watts" style="height: 100px">
    <div>
      <h1 style="font-size: 2.5em; margin: 0;">Diagnostic batterie Lithium-ion</h1>
      <p style="font-size: 1.6em">{getDate()}</p>
    </div>
  </div>

  <div class="panels-container">
    <div class="left-panels-container">
      <ClientPanel bind:open={client_panel_open}></ClientPanel>
      <BatteryPanel bind:open={battery_panel_open}></BatteryPanel>
    </div>
    <div class="right-panels-container hide-on-screen">
      <DiagPanel></DiagPanel>
    </div>
  </div>
  
  <h2 class="hide-on-screen chart-title">Cycle de charge-décharge</h2>

  <div class="chart-container">
    <BattChart />
  </div>

  <div class="export-buttons hide-on-print" style="text-align: right;">
    <!-- <a href={apiUrl + "/battery-state"} download={jsonFileName} target="_blank">raw</a> -->
    <button on:click={downloadRaw}><i class="fa-solid fa-file-export"></i></button>
    <!-- <a href={apiUrl + "/get-csv?filename=" + csvFileName} download={csvFileName}>csv</a> -->
    <button on:click={downloadCSV}><i class="fa-solid fa-file-csv"></i></button>
    &nbsp;
    <button on:click={printPage}><i class="fa-solid fa-print"></i></button>
  </div>
  
  <div class="hide-on-print">
    <div class="control-container">
      <div>
        <BattControl2 />
      </div>
      <div>
        <BattState />
      </div>
      <!-- <div class="border-left">
        <BattCapacity/>
      </div> -->
    </div>
  </div>

  <p id="version-label">v {import.meta.env.VITE_VERSION}</p>

  <ErrorModal />
</main>



<style>
  .hide-on-screen {
    display: none;
  }

  .panels-container {
    display: flex;
  }

  .left-panels-container {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  .chart-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    height: 380px;
    margin: 25px 16px 0 16px;
  }

  .control-container {
    display: flex;
    align-items: center;
    max-width: fit-content;
    /* justify-content: space-around; */
    margin: auto;
  }
  .control-container div {
    /* padding: 0px 50px 0px 50px; */
    margin-right: 50px;
  }

  #version-label {
    position: fixed;
    bottom: -8px;
    right: 10px;
    font-weight: bold;
  }

  .right-panels-container {
    width: 50%;
    margin: 0;
  }

  .export-buttons {
    position: relative;
    right: 70px;
    top: -14px;
  }

  .export-buttons button {
    font-size: 0.9em;
    padding: 2px 4px;
  }

  @media print {
    .print-header {
      display: flex;
      justify-content: space-between;
      text-align: right;
      margin-bottom: 32px;
      margin-right: 5%;
    }

    .chart-title {
      display: block;
      font-size: 1.6em;
      text-align: center;
      margin-top: 32px;
    }

    .chart-container {
      display: block;
      position: absolute;
      bottom: 120px;
    }

    .panels-container {
      display: flex;
      /* justify-content: space-around; */
      background-color: rgb(191, 238, 207);
    }

    .right-panels-container {
      display: block;
    }

    .hide-on-print {
      display: none;
    }

    button {
      display: none;
    }
  }
</style>