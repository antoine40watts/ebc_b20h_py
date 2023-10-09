<script>
    import { batteryData } from "../stores.js";
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
                data: $batteryData.voltage,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            },
            {
                label: 'Current',
                yAxisID: 'cAxis',
                borderColor: 'rgb(200, 200, 75)',
                data: $batteryData.current,
                // pointStyle: false,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            },
            {
                label: 'mAh',
                yAxisID: 'mahAxis',
                borderColor: 'rgb(80, 230, 152)',
                data: $batteryData.mah,
                // pointStyle: false,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            }
        ],
        labels: $batteryData.time,
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
</script>


<div class="container">
{#if $batteryData.voltage.length > 0}
    <div class="chart-container">
        <Line options={options} data={chartData} />
    </div>
    <div class="export-button">
        Export 
        <a href="http://localhost:8000/battery-state" download={jsonFileName} target="_blank"><button>raw</button></a>
        <a href={"http://localhost:8000/get-csv?filename=" + csvFileName}
            download={csvFileName}><button>csv</button></a>
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
        top: 160px;
        margin-left: -118px;
        right: 80px;
        text-align: right;
        /* margin-right: 16px; */
    }
</style>