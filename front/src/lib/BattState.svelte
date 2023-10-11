<script>
    import { batteryData } from "../stores.js";

    $: voltage = $batteryData.voltage.slice(-1)[0];
    $: current = $batteryData.current.slice(-1)[0];
    $: mah = $batteryData.mah.slice(-1)[0];

    function getDecimalPart(n) {
        return parseInt(10 * (n - parseInt(n)))
    }

    const batteryStates = ["Idle", "Charging", "Discharging"];
    const statesColor = ["grey", "#3aaa35", "red"]


    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;

    async function stopDevices() {
        const url = apiUrl + "/stop";
        
        let resultMessage = '';

        try {
            const response = await fetch(url, {
                method: 'POST',
                // headers: {'Content-Type': 'application/json'},
                // body: JSON.stringify(rpc_data),
            });
        
            if (!response.ok) {
                throw new Error('RPC request failed');
            }
            
            const data = await response.json();
            resultMessage = data.message;
        } catch (error) {
            console.error('Error making RPC call:', error);
            resultMessage = 'RPC call failed';
        }
    }
</script>


<div class="container">
    <p class="state" style="color: {statesColor[$batteryData.state]};">
        {batteryStates[$batteryData.state]}
        {#if $batteryData.state != 0}
            <button class="button-stop" on:click={stopDevices}>STOP</button>
        {/if}
    </p>
    <span style="font-size: 3.5rem">{parseInt(voltage)}</span>
    <span style="font-size: 2.5rem">.{getDecimalPart(voltage)} V</span>
    
    <span style="font-size: 1.5rem; margin: 16px;">@</span>
    <span style="font-size: 3rem">{parseInt(current)}</span>
    <span style="font-size: 2rem">.{getDecimalPart(current)} A</span>
    
    <p style="font-size: 2.5em">{mah} <span style="font-size: 0.6em">mAh</span></p>
</div>

<style>
    .container {
        /* max-width: fit-content; */
        text-align: center;
        /* background-color: #df2020; */
    }
    .container p {
        margin: 8px;
    }
    .state {
        font-size: 2.2em;
        font-weight: 500;
    }
    
    .button-stop {
        margin: 0 4px 0 4px;
        border-radius: 20px;
        border: none;
        padding: 8px;
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        background-color: tomato;
    }
    .button-stop:hover {
        background-color: orangered;
    }
    .button-stop:active {
        background-color: crimson;
    }
</style>