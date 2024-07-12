<script>
    import { deviceData } from "../stores.js";
    import idleIcon from "../assets/batt_idle.png";
    import chargeIcon from "../assets/batt_charging.png";
    import { tooltip } from "../tooltip.js";

    $: voltage = $deviceData.voltage;
    $: current = $deviceData.current;
    $: mah = $deviceData.mah;

    function getDecimalPart(n) {
        return parseInt( Math.round(10 * (n - Math.floor(n))) % 10, 10 )
    }

    function getIntegerPart(n) {
        let int_part = Math.floor(n);
        let dec_part = 10 * (n - int_part);
        if (Math.round(dec_part) >= 10)
            int_part++;
        return int_part;
    }

    const batteryStates = ["En attente", "En charge", "Décharge"];
    const statesColor = ["grey", "#3aaa35", "red"]

    // const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

</script>


<div class="container">
    <p class="state" style="color: {statesColor[$deviceData.battery_state]};">
        {#if $deviceData.battery_state == 0}
            <img class="battery-icon" src={idleIcon}>
        {:else if $deviceData.battery_state == 1}
            <img class="battery-icon" src={chargeIcon}>
        <!-- <button class="button-stop" on:click={stopDevices}>ARRÊT</button> -->
        {/if}
        {batteryStates[$deviceData.battery_state]}
    </p>
    <span style="font-size: 3.5rem">{getIntegerPart(voltage)}</span>
    <span style="font-size: 2.5rem">.{getDecimalPart(voltage)} V</span>
    
    <span style="font-size: 1.5rem; margin: 16px;">@</span>
    <span style="font-size: 3rem">{getIntegerPart(current)}</span>
    <span style="font-size: 2rem">.{getDecimalPart(current)} A</span>
    
    <p style="font-size: 2.5em; color: #3aaa35;">{Math.round(mah)} <span style="font-size: 0.6em">mAh</span></p>
</div>

<style>
    .container {
        position: relative;
        /* max-width: fit-content; */
        text-align: center;
        width: 380px;
    }

    .container p {
        margin: 8px;
    }

    .state {
        font-size: 2.2em;
        font-weight: 500;
    }

    .battery-icon {
        scale: 3;
        position: fixed;
        top: 40%;
        left: 50%;
        transform: translate(-10%, 0);
        filter: opacity(0.1);
        z-index: -9999;
    }

    @media print{
        .container {
            display: none;
        }
    }
</style>