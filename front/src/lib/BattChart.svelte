<script>
    import { deviceData } from "../stores.js";
    import { deviceParameters } from "../stores.js";
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
        labels: $deviceData.time,
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
        ]
    }


    $: options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: { 
                    text: 'Time (s)',
                    display: true,
                },
                type: 'linear',
                max: Math.ceil($deviceData.time[$deviceData.time.length - 1]),
            },
            vAxis: {
                title: { 
                    text: 'Voltage',
                    align: 'end',
                    display: true,
                },
                type: 'linear',
                suggestedMax: $deviceParameters.charge_v + 1,
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
                max: Math.max($deviceParameters.discharge_c, $deviceParameters.charge_c) + 1,
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
</script>

<div class="container">
{#if $deviceData.voltage.length > 0}
    <div class="chart-container">
        <Line options={options} data={chartData} />
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

    @media print {
        .container {
            /* transform: rotate(90deg); */
            /* display: flow; */
            position: absolute;
            top: 120px;
            left: 0;
        }
    }
</style>