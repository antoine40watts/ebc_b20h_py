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
</script>


<div class="container">
    <p class="state" style="color: {statesColor[$batteryData.state]};">
        {batteryStates[$batteryData.state]}
    </p>
    <span style="font-size: 4em">{parseInt(voltage)}</span>
    <span style="font-size: 2.5em">.{getDecimalPart(voltage)} V</span>
    
    <span style="font-size: 1.5em; margin: 16px;">@</span>
    <span style="font-size: 3em">{parseInt(current)}</span>
    <span style="font-size: 2em">.{getDecimalPart(current)} A</span>
    
    <p style="font-size: 2.5em">{mah} <span style="font-size: 0.6em">mAh</span></p>
</div>

<style>
    .container {
        max-width: fit-content;
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
</style>