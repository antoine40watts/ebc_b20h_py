<script>
    import { deviceData } from "../stores.js";
    import idleIcon from "../assets/batt_idle.png";

    $: voltage = $deviceData.voltage;
    $: current = $deviceData.current;
    $: mah = $deviceData.mah;

    function getDecimalPart(n) {
        return parseInt(10 * (n - parseInt(n)))
    }

    const batteryStates = ["En attente", "En charge", "Décharge"];
    const statesColor = ["grey", "#3aaa35", "red"]


    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

    // async function stopDevices() {
    //     const url = apiUrl + "/stop";
        
    //     let resultMessage = '';

    //     try {
    //         const response = await fetch(url, {
    //             method: 'POST',
    //             // headers: {'Content-Type': 'application/json'},
    //             // body: JSON.stringify(rpc_data),
    //         });
        
    //         if (!response.ok) {
    //             throw new Error('RPC request failed');
    //         }
            
    //         const data = await response.json();
    //         resultMessage = data.message;
    //     } catch (error) {
    //         console.error('Error making RPC call:', error);
    //         resultMessage = 'RPC call failed';
    //     }
    // }
</script>


<div class="container">
    <p class="state" style="color: {statesColor[$deviceData.battery_state]};">
        {#if $deviceData.battery_state == 0}
            <img class="idle-icon" src={idleIcon}>
            {batteryStates[$deviceData.battery_state]}
        {:else}
            {batteryStates[$deviceData.battery_state]}
            <!-- <button class="button-stop" on:click={stopDevices}>ARRÊT</button> -->
        {/if}
    </p>
    <span style="font-size: 3.5rem">{Math.floor(voltage)}</span>
    <span style="font-size: 2.5rem">.{getDecimalPart(voltage)} V</span>
    
    <span style="font-size: 1.5rem; margin: 16px;">@</span>
    <span style="font-size: 3rem">{Math.floor(current)}</span>
    <span style="font-size: 2rem">.{getDecimalPart(current)} A</span>
    
    <p style="font-size: 2.5em; color: #3aaa35;">{mah} <span style="font-size: 0.6em">mAh</span></p>
</div>

<style>
    .container {
        position: relative;
        /* max-width: fit-content; */
        text-align: center;
    }

    .container p {
        margin: 8px;
    }

    .state {
        font-size: 2.2em;
        font-weight: 500;
    }

    .idle-icon {
        /* translate: -50% 0; */
        scale: 0.5;
        position: absolute;
        top: -35px;
        right: -38px;
        filter: opacity(0.9);
    }

    @media print{
        .container {
            display: none;
        }
    }
</style>