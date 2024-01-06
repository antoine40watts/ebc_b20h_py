<script>
    import { deviceParameters } from "../stores.js";
    import { deviceData } from "../stores.js";
    // import Accordion from './Accordion.svelte';

</script>

<h3>Conditions de test</h3>
<div >
    <table>
        <tr>
            <td nowrap>Courant de charge</td><td>{$deviceParameters.charge_c} A</td>
        </tr>
        <tr>
            <td nowrap>Courant de décharge</td><td>{$deviceParameters.discharge_c} A</td>
        </tr>
        <tr>
            <td>Tension minimale</td><td>{$deviceParameters.discharge_v} V</td>
        </tr>
        <tr>
            <td>Tension maximale</td><td>{$deviceParameters.charge_v} V</td>
        </tr>
    </table>
</div>

<h3>Résultats</h3>
<div>
    <table>
        <tr>
            <td>Capacité mesurée</td>
            <td>
                <!-- {#if $deviceData.capacity > 0} -->
                <span style="font-size: 1.5em; font-weight: bold;">{Math.round($deviceData.capacity / 10) / 100} Ah</span>&nbsp;&nbsp;
                <span style="font-size: 1.2em; font-weight: bold;">({Math.round($deviceParameters.cells_s * 3.7 * $deviceData.capacity / 100) / 10 } Wh)</span>
                <!-- {:else}
                en attente
                {/if} -->
            </td>
        </tr>
        <!-- {#if $deviceData.capacity > 0} -->
        <tr>
            <td></td><td nowrap>{Math.round(100 * $deviceData.capacity / $deviceParameters.original_capacity)}% de la capacité originale</td>
        </tr>
        <!-- {/if} -->
    </table>
</div>

<style>
    h3 {
        display:flex;
        height: 38px;
        align-items: center;
        margin: 0;
        padding-left: 16px;
    }

    div {
        padding:8px;
        padding-left: 26px;
    }

    table td {
      height: 1.6em;
      width: 180px;
    }
</style>
