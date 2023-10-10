<script>
  // import { store } from './stores.js';

  import IDBar from "./lib/IDBar.svelte";
  import BattState from "./lib/BattState.svelte";
  import BattChart from "./lib/BattChart.svelte";
  import BattControl from "./lib/BattControl.svelte";

  let cells_s = 1;
  let cells_p = 1;
  $: charge_v = Math.round(cells_s * 4.20 * 100) / 100;
  // $: charge_c = cells_p * 0.5;
  $: discharge_v = Math.round(cells_s * 2.70 * 100) / 100;
  // $: discharge_c = cells_p * 0.5;

</script>


<main>
  <IDBar bind:cells_s bind:cells_p />

  <div class="chart-container">
    <BattChart />
  </div>

  <div>
    <div class="control-container">
      <div style="padding-right: 40px;">
        <!-- <BattControl {charge_v} {charge_c} {discharge_v} {discharge_c} /> -->
        <BattControl {charge_v} {discharge_v} />
      </div>
      <div class="border-left" style="padding-left: 40px">
        <BattState />
      </div>
    </div>
  </div>
</main>



<style>
  .chart-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    height: 350px;
    margin: 25px 16px 32px 16px;
  }

  .control-container {
    display: flex;
    justify-content: space-around;
    max-width: fit-content;
    margin: auto;
  }

  .border-left {
    border-left: 1px solid rgba(10, 59, 23, 0.4);
  }

  @media print{
    .border-left {
      display: none;
    }
  }
</style>