<script>

    import Accordion from './Accordion.svelte'
    import { deviceParameters } from "../stores.js";

    export let open = false;

    let battery_brand = "";
    let battery_model = "";
    let cells_s = 10;
    let cells_p = 1;
    let original_capacity = 0;  // amps
    let battery_year = 1999;
    let battery_bike = "";

    let v_table = [0, 3.7, 7.4, 11.1, 12, 18.5, 22.2, 24, 29.6, 33.3, 36, 40.7, 44.4, 48, 51.8, 55.5, 60]

    function updateParams() {
      deviceParameters.update((params) => {
          params.charge_v = Math.round(4.2 * cells_s * 100) / 100;
          params.discharge_v = Math.round(2.7 * cells_s * 100) / 100;
          params.original_capacity = original_capacity * 1000;
          params.cells_s = cells_s;
          return params;
      });
  }

</script>

<Accordion bind:open={open} flex_size={2}>
    <span slot="header-icon"><i class="fa-solid fa-car-battery"></i></span>
    <span slot="header-title">Batterie</span>
    <div class="align-center" slot="details">
      <table style="width: 800px">
        <tr>
          <td><label for="battery-brand">Marque</label></td>
          <td><input type="text" id="battery-brand" name="battery-brand" size="16"
              placeholder="non renseigné"
              bind:value={battery_brand} /></td>
          <td><label for="battery-model">Modèle</label></td>
          <td><input type="text" id="battery-model" name="battery-model" size="16"
            placeholder="non renseigné"
            bind:value={battery_model} /></td>
        </tr><tr>
          <td><label for="battery-year">Année</label></td>
          <td><input type="number" id="battery-year" name="battery-year" size="5"
              bind:value={battery_year} 
              min="1999" step="1" style="width: 70px;" /></td>
          <td><label for="battery-bike">Vélo</label></td>
          <td><input type="text" id="battery-bike" name="battery-bike" size="16"
              placeholder="non renseigné"
              bind:value={battery_bike} /></td>
        </tr><tr>
            <td><label for="battery-capacity">Capacité</label></td>
            <!-- <td><input type="text" id="battery-capacity" name="battery-capacity" size="8"/></td> -->
            <td><input type="number" id="battery-capacity" name="battery-capacity" size="6"
              style="width: 70px;"
              min="1" step="1" bind:value={original_capacity} on:input={updateParams} />Ah
            &nbsp;&nbsp;&nbsp;(<span style="font-weight: bold">{Math.round(original_capacity * cells_s * 3.7)}</span> Wh)</td>
        </tr><tr>
            <td><label for="cells_s">Cellules Série</label></td>
            <td><input type="number" id="cells_s" name="cells_s" size="3"
                    style="width: 50px;"
                    min="4" max="16" bind:value={cells_s} on:input={updateParams} /></td>
            <td>Tension nominale<td>
            <td style="font-weight: bold; font-size: 1.4em;">{v_table[cells_s]} V</td>
        </tr>
      </table>

    </div>
</Accordion>


<style>
    table td {
      height: 1.6em;
    }

    .align-center {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        /* flex-direction: column; */
    }

    input {
        margin-left: 4px;
        margin-right: 16px;
        background-color: white;
        border-radius: 16px;
        border: 0;
    }
</style>