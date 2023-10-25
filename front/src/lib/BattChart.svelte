<script>
    import { deviceData } from "../stores.js";
    import { Line } from "svelte-chartjs";

    import {
        Chart as ChartJS,
        Title,
        Tooltip,
        Legend,
        LineController,
        LineElement,
        LinearScale,
        PointElement,
    } from "chart.js";

    ChartJS.register(
        Title,
        Tooltip,
        Legend,
        LineController,
        LineElement,
        LinearScale,
        PointElement,
    );


    $: chartData = {
        datasets: [
            {
                label: 'Voltage',
                yAxisID: 'vAxis',
                // fill: true,
                backgroundColor: 'rgba(225, 204,230, .3)',
                borderColor: 'rgb(75, 192, 192)',
                data: $deviceData.voltage,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            },
            {
                label: 'Current',
                yAxisID: 'cAxis',
                borderColor: 'rgb(200, 200, 75)',
                data: $deviceData.current,
                // pointStyle: false,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            },
            {
                label: 'mAh',
                yAxisID: 'mahAxis',
                borderColor: 'rgb(80, 230, 152)',
                data: $deviceData.mah,
                // pointStyle: false,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            }
        ],
        labels: $deviceData.time,
    }


    let options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: { 
                    text: 'Time (s)',
                    display: true,
                },
                type: 'linear',
            },
            vAxis: {
                title: { 
                    text: 'Voltage',
                    align: 'end',
                    display: true,
                },
                type: 'linear',
                suggestedMax: 56,
                beginAtZero: true,
            },
            cAxis: {
                title: { 
                    text: 'Amp',
                    align: 'end',
                    display: true,
                },
                grid: {
                    drawOnChartArea: false, // only want the grid lines for one axis to show up
                },
                type: 'linear',
                max: 20,
                beginAtZero: true,
            },
            mahAxis: {
                title: { 
                    text: 'mAh',
                    align: 'end',
                    display: true,
                },
                type: 'linear',
                position: 'right',
                beginAtZero: true,
            },
        },
        animation: false,
    };


    let csvFileName = "battery_data.csv";
    let jsonFileName = "battery_data.json";

    const apiUrl = import.meta.env.VITE_PROD === 'true' ? import.meta.env.VITE_API_PROD_URL : import.meta.env.VITE_API_DEV_URL;


    // function downloadCSV() {
    //     const csvContent = "data:text/csv;charset=utf-8," + $batteryData.voltage.map(row => row.join(",")).join("\n");
    //     const encodedUri = encodeURI(csvContent);
    //     const link = document.createElement("a");
    //     link.setAttribute("href", encodedUri);
    //     link.setAttribute("download", "data.csv");
    //     document.body.appendChild(link);
    //     link.click();
    //     document.body.removeChild(link);
    // }

    function downloadRaw() {
        let url = apiUrl + "/battery-state";
        window.open(url, '_blank');
    }

    function downloadCSV() {
        let url = apiUrl + "/get-csv?filename=" + csvFileName;
        window.open(url, '_blank');
    }
</script>


<h2>Courbe de décharge</h2>

<div class="container">
{#if $deviceData.voltage.length > 0}
    <div class="chart-container">
        <Line options={options} data={chartData} />
    </div>
    <div class="export-button">
        Export 
        <!-- <a href={apiUrl + "/battery-state"} download={jsonFileName} target="_blank">raw</a> -->
        <button on:click={downloadRaw}>raw</button>
        <!-- <a href={apiUrl + "/get-csv?filename=" + csvFileName} download={csvFileName}>csv</a> -->
        <button on:click={downloadCSV}>csv</button>
    </div>
{:else}
    <div class="error-message">
        <p>No data recieved...</p>
    </div>
{/if}
</div>


<style>
    .container {
        min-width: 400px;
        /* background-color: #646cffaa; */
        display: flex;
        flex-grow: 16;
        flex-direction: row;
        justify-content: center;
        align-items: center;
    }
    .chart-container {
        flex-grow: 1;
        width: 1px; /* Works because of flex-grow */
        height: 100%;
    }
    .error-message {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .export-button {
        /* position: relative; */
        position: relative;
        /* transform: translateX(-100px); */
        top: 180px;
        margin-left: -118px;
        right: 80px;
        text-align: right;
        /* margin-right: 16px; */
    }

    h2 {
        display: none;
    }

    @media print {
    h2 {
        display: block;
        text-align: left;
    }
    .export-button {
        display: none;
    }
    .chart-container {
        /* transform: rotate(90deg);
        display: flow;*/
        /* position: absolute;
        top: 200;
        left: 0; */
    }
    .container {
        /* transform: rotate(90deg); */
        /* display: flow; */
        position: absolute;
        top: 120px;
        left: 0;
    }
  }
</style>